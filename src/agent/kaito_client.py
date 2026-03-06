"""
Custom OpenAI Chat Client for KAITO RAG Engine compatibility.
"""

from collections.abc import Mapping, Sequence
from typing import Any
from agent_framework import Content, Message
from agent_framework.openai import OpenAIChatClient


class KAITOChatClient(OpenAIChatClient):
    """Custom OpenAI Chat Client optimized for KAITO RAG Engine compatibility."""

    def _prepare_content_for_openai(self, content: Content) -> dict[str, Any]:
        """Parse content into the OpenAI format, returning plain text for text content."""
        if content.type == "text":
            return {"type": "text", "text": content.text or ""}
        return super()._prepare_content_for_openai(content)

    def _prepare_messages_for_openai(
        self,
        chat_messages: Sequence[Message],
        role_key: str = "role",
        content_key: str = "content",
    ) -> list[dict[str, Any]]:
        """Override to ensure compatibility with KAITO RAG Engine."""
        messages = super()._prepare_messages_for_openai(
            chat_messages, role_key, content_key
        )

        # KAITO RAG Engine expects content as a plain string, not a list
        for msg in messages:
            if "content" in msg and isinstance(msg["content"], list):
                if len(msg["content"]) == 1 and isinstance(msg["content"][0], dict):
                    text = msg["content"][0].get("text")
                    if text is not None:
                        msg["content"] = text

        return messages

    def _prepare_options(
        self, messages: Sequence[Message], options: Mapping[str, Any]
    ) -> dict[str, Any]:
        """Override to handle system messages when routing through the RAG Engine.

        The KAITO RAG Engine uses LlamaIndex's ContextChatEngine which injects
        its own system message containing retrieved RAG context. If we also send
        the agent's instructions as a system message, the model receives two
        consecutive system messages, which models like Gemma reject (they require
        strict user/assistant alternation).

        When index_name is present in extra_body, we fold the instructions into
        the user message so the model still receives behavioral guidelines
        without creating duplicate system messages.
        """
        extra_body = options.get("extra_body", {})
        is_rag_request = extra_body.get("index_name") if extra_body else False

        if is_rag_request and options.get("instructions"):
            # Move instructions from system message into a preamble on the user message
            instructions = options.get("instructions")
            options = {k: v for k, v in options.items() if k != "instructions"}

            # Prepend instructions to the first user message's content
            updated_messages = list(messages)
            for i, msg in enumerate(updated_messages):
                if msg.role == "user" and msg.contents:
                    from agent_framework import Content

                    original_text = msg.contents[0].text or ""
                    combined_text = f"[Instructions: {instructions}]\n\n{original_text}"
                    new_contents = [Content.from_text(combined_text)] + list(
                        msg.contents[1:]
                    )
                    updated_messages[i] = Message(role="user", contents=new_contents)
                    break
            messages = updated_messages

        result = super()._prepare_options(messages, options)

        # The agent framework translates max_tokens → max_completion_tokens
        # (via OPTION_TRANSLATIONS), but the KAITO RAG Engine only recognizes
        # max_tokens for context-window budgeting.  Without it the
        # ContextSelectionProcessor adds unlimited RAG context, inflating the
        # downstream inference request body beyond what the body-based-router
        # ext-proc can inspect, which prevents model-header extraction and
        # causes a 404 from the gateway.
        if is_rag_request and "max_completion_tokens" in result:
            result["max_tokens"] = result.pop("max_completion_tokens")

        return result
