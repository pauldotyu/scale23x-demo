#!/usr/bin/env python3
"""
Format SCALE23x schedule JSON into document format for indexing.
"""

import json
from pathlib import Path
from typing import Any


def format_schedule_for_indexing(
    schedule_file: Path, output_file: Path, index_name: str = "schedule_index"
) -> dict[str, Any]:
    """
    Read schedule.json and format it for document indexing.

    Args:
        schedule_file: Path to input schedule.json
        output_file: Path to output formatted JSON
        index_name: Name of the index

    Returns:
        Formatted document structure
    """
    # Read schedule data
    with open(schedule_file, "r", encoding="utf-8") as f:
        schedule_data = json.load(f)

    documents: list[dict[str, Any]] = []

    for item in schedule_data:
        title = str(item.get("title", "")).strip()
        description = str(item.get("description", "")).strip()
        speaker = str(item.get("speaker", "")).strip()
        url = str(item.get("url", "")).strip()
        speaker_url = str(item.get("speaker_url", "")).strip()
        topic = str(item.get("topic", "")).strip()
        audience = str(item.get("audience", "")).strip()
        location = str(item.get("location", "")).strip()
        date = str(item.get("date", "")).strip()
        start = str(item.get("start", "")).strip()
        end = str(item.get("end", "")).strip()

        text_parts = [
            part
            for part in (title, description, speaker, topic, audience, location)
            if part
        ]
        text = " ".join(text_parts).strip()

        documents.append(
            {
                "text": text,
                "metadata": {
                    "title": title,
                    "description": description,
                    "url": url,
                    "speakers": [
                        {
                            "name": speaker,
                            "url": speaker_url,
                        }
                    ],
                    "topic": topic,
                    "audience": audience,
                    "location": location,
                    "date": date,
                    "start": start,
                    "end": end,
                },
            }
        )

    formatted = {
        "index_name": index_name,
        "documents": documents,
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(formatted, f, ensure_ascii=False, indent=2)

    return formatted


def main():
    """Main function to format schedule data."""
    schedule_file = Path(__file__).parent / "output/schedule.json"
    output_file = Path(__file__).parent / "output/schedule_index.json"
    index_name = "schedule_index"

    if not schedule_file.exists():
        print(f"❌ Error: {schedule_file} not found")
        print("Run parse_schedule.py first to generate schedule.json")
        return

    print(f"Reading schedule from {schedule_file}...")
    formatted = format_schedule_for_indexing(schedule_file, output_file, index_name)
    print(f"✅ Wrote {len(formatted['documents'])} documents to {output_file}")


if __name__ == "__main__":
    main()
