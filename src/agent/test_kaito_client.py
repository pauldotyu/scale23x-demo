"""Tests for KAITOChatClient message handling."""

from unittest.mock import patch
from agent_framework import Content, Message
from kaito_client import KAITOChatClient


def make_client():
    """Create a KAITOChatClient with a dummy config (no real API calls)."""
    return KAITOChatClient(model_id="gemma-3-27b-instruct", api_key="test-key")


class TestPrepareMessagesForOpenAI:
    """Test that content is flattened to plain strings for KAITO compatibility."""

    def test_text_content_flattened(self):
        client = make_client()
        messages = [Message("user", [Content.from_text("hello")])]
        result = client._prepare_messages_for_openai(messages)
        assert result[0]["content"] == "hello"

    def test_non_text_content_unchanged(self):
        client = make_client()
        messages = [Message("user", [Content.from_text("hello")])]
        result = client._prepare_messages_for_openai(messages)
        # Should be a plain string, not a list
        assert isinstance(result[0]["content"], str)


class TestPrepareOptionsRAGPath:
    """Test that instructions are folded into the user message for RAG requests."""

    def test_rag_request_moves_instructions_to_user_message(self):
        client = make_client()
        messages = [
            Message("user", [Content.from_text("What sessions are about KAITO?")])
        ]
        options = {
            "instructions": "You are a helpful assistant.",
            "extra_body": {
                "index_name": "schedule_index",
                "model": "gemma-3-27b-instruct",
            },
            "model_id": "gemma-3-27b-instruct",
        }

        result = client._prepare_options(messages, options)

        # Instructions should NOT be in the final options (no system message)
        prepared_messages = result["messages"]
        system_messages = [m for m in prepared_messages if m.get("role") == "system"]
        assert (
            len(system_messages) == 0
        ), f"Expected no system messages, got {system_messages}"

        # The user message should contain the instructions
        user_messages = [m for m in prepared_messages if m.get("role") == "user"]
        assert len(user_messages) == 1
        assert "[Instructions:" in user_messages[0]["content"]
        assert "What sessions are about KAITO?" in user_messages[0]["content"]

    def test_rag_request_without_instructions_unchanged(self):
        client = make_client()
        messages = [Message("user", [Content.from_text("hello")])]
        options = {
            "extra_body": {
                "index_name": "schedule_index",
                "model": "gemma-3-27b-instruct",
            },
            "model_id": "gemma-3-27b-instruct",
        }

        result = client._prepare_options(messages, options)

        prepared_messages = result["messages"]
        system_messages = [m for m in prepared_messages if m.get("role") == "system"]
        assert len(system_messages) == 0

        user_messages = [m for m in prepared_messages if m.get("role") == "user"]
        assert user_messages[0]["content"] == "hello"


class TestPrepareOptionsDirectPath:
    """Test that instructions remain as system messages for non-RAG requests."""

    def test_direct_request_keeps_instructions_as_system(self):
        client = make_client()
        messages = [Message("user", [Content.from_text("Tell me about SCALE")])]
        options = {
            "instructions": "You are a helpful assistant.",
            "model_id": "gemma-3-27b-instruct",
        }

        result = client._prepare_options(messages, options)

        prepared_messages = result["messages"]
        system_messages = [m for m in prepared_messages if m.get("role") == "system"]
        assert len(system_messages) == 1
        assert "helpful assistant" in system_messages[0]["content"]

        user_messages = [m for m in prepared_messages if m.get("role") == "user"]
        assert "[Instructions:" not in user_messages[0]["content"]

    def test_direct_request_without_instructions(self):
        client = make_client()
        messages = [Message("user", [Content.from_text("hello")])]
        options = {
            "model_id": "gemma-3-27b-instruct",
        }

        result = client._prepare_options(messages, options)

        prepared_messages = result["messages"]
        system_messages = [m for m in prepared_messages if m.get("role") == "system"]
        assert len(system_messages) == 0


class TestMaxTokensTranslation:
    """Test that max_completion_tokens is converted back to max_tokens for RAG requests."""

    def test_rag_request_uses_max_tokens(self):
        """RAG requests should send max_tokens, not max_completion_tokens,
        because the KAITO RAG Engine only recognizes max_tokens for
        context-window budgeting."""
        client = make_client()
        messages = [Message("user", [Content.from_text("hello")])]
        options = {
            "max_tokens": 1024,
            "extra_body": {
                "index_name": "schedule_index",
                "model": "gemma-3-27b-instruct",
            },
            "model_id": "gemma-3-27b-instruct",
        }

        result = client._prepare_options(messages, options)

        assert "max_tokens" in result, "RAG requests must use max_tokens"
        assert (
            "max_completion_tokens" not in result
        ), "max_completion_tokens should be converted to max_tokens for RAG"
        assert result["max_tokens"] == 1024

    def test_direct_request_keeps_max_completion_tokens(self):
        """Non-RAG requests should keep the framework's max_completion_tokens
        translation since the OpenAI SDK and vLLM both support it."""
        client = make_client()
        messages = [Message("user", [Content.from_text("hello")])]
        options = {
            "max_tokens": 1024,
            "model_id": "gemma-3-27b-instruct",
        }

        result = client._prepare_options(messages, options)

        assert "max_completion_tokens" in result
        assert result["max_completion_tokens"] == 1024
