from __future__ import annotations
import json
import re
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

PRESENTATIONS_URL = "https://www.socallinuxexpo.org/scale/23x/presentations"


@dataclass(frozen=True)
class Presentation:
    title: str
    url: str
    speaker: str
    speaker_url: str
    description: str
    topic: str
    audience: str
    location: str
    date: str
    start: str
    end: str


def normalize_href(raw_href: object) -> str | None:
    if isinstance(raw_href, list):
        return raw_href[0] if raw_href else None
    if isinstance(raw_href, str):
        return raw_href
    return None


def find_next_page_url(soup: BeautifulSoup, current_url: str) -> str | None:
    next_link = soup.find(
        "a",
        rel=lambda value: (
            "next" in value
            if isinstance(value, list)
            else bool(value and "next" in value)
        ),
    )
    if next_link:
        href = normalize_href(next_link.get("href"))
        if href:
            return urljoin(current_url, href)

    for link in soup.find_all("a"):
        text = (link.get_text() or "").strip().lower()
        raw_title = link.get("title")
        if isinstance(raw_title, list):
            raw_title = raw_title[0] if raw_title else ""
        title = (raw_title or "").strip().lower()
        if "next page" in text or text == "next" or "next page" in title:
            href = normalize_href(link.get("href"))
            if href:
                return urljoin(current_url, href)
    return None


def build_page_url(base_url: str, page_index: int) -> str:
    parsed = urlparse(base_url)
    query = parse_qs(parsed.query)
    query["page"] = [str(page_index)]
    return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))


def discover_page_urls(soup: BeautifulSoup, current_url: str) -> list[str]:
    page_indices: set[int] = set()
    for link in soup.find_all("a", href=True):
        href = link["href"]
        href_text = "".join(href) if isinstance(href, list) else str(href)
        if "page=" not in href_text:
            continue
        absolute_url = urljoin(current_url, href_text)
        parsed = urlparse(absolute_url)
        query = parse_qs(parsed.query)
        for value in query.get("page", []):
            if value.isdigit():
                page_indices.add(int(value))

    if not page_indices:
        return []

    return [build_page_url(current_url, index) for index in sorted(page_indices)]


def extract_presentations(soup: BeautifulSoup, page_url: str) -> Iterable[Presentation]:
    for heading in soup.select("h3"):
        link = heading.find("a")
        if not link:
            continue
        href = normalize_href(link.get("href"))
        if not href:
            continue
        absolute_url = urljoin(page_url, href)
        if "/scale/23x/presentations/" not in absolute_url:
            continue
        title = link.get_text(strip=True)
        if not title:
            continue
        speaker = ""
        speaker_url = ""
        description = ""
        sibling = heading.find_next_sibling()
        if sibling and sibling.name == "div":
            speaker = sibling.get_text(" ", strip=True)
            for link in sibling.find_all("a", href=True):
                href = normalize_href(link.get("href"))
                if href:
                    speaker_url = urljoin(page_url, href)
                    break
            description_node = sibling.find_next_sibling()
            if description_node:
                description = description_node.get_text(" ", strip=True)
                description = description.replace("\u2011", "-")
        yield Presentation(
            title=title,
            url=absolute_url,
            speaker=speaker,
            speaker_url=speaker_url,
            description=description,
            topic="",
            audience="",
            location="",
            date="",
            start="",
            end="",
        )


def fetch_all_presentations(start_url: str) -> list[Presentation]:
    session = requests.Session()
    session.headers.update(
        {"User-Agent": "scale23x-demo/1.0 (+https://www.socallinuxexpo.org/)"}
    )

    seen_presentations: set[str] = set()
    presentations: list[Presentation] = []

    response = session.get(start_url, timeout=30)
    response.raise_for_status()
    first_soup = BeautifulSoup(response.text, "html.parser")

    page_urls = discover_page_urls(first_soup, start_url)
    if not page_urls:
        page_urls = [start_url]

    for presentation in extract_presentations(first_soup, start_url):
        if presentation.url in seen_presentations:
            continue
        presentations.append(presentation)
        seen_presentations.add(presentation.url)

    for page_url in page_urls:
        if page_url == start_url:
            continue
        response = session.get(page_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for presentation in extract_presentations(soup, page_url):
            if presentation.url in seen_presentations:
                continue
            presentations.append(presentation)
            seen_presentations.add(presentation.url)

    if len(page_urls) == 1:
        next_url = find_next_page_url(first_soup, start_url)
        while next_url:
            response = session.get(next_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for presentation in extract_presentations(soup, next_url):
                if presentation.url in seen_presentations:
                    continue
                presentations.append(presentation)
                seen_presentations.add(presentation.url)
            next_url = find_next_page_url(soup, next_url)

    def enrich(p: Presentation) -> Presentation:
        resp = session.get(p.url, timeout=30)
        resp.raise_for_status()
        text = BeautifulSoup(resp.text, "html.parser").get_text(" ")
        topic = m.group(1).strip() if (m := re.search(r"Topic:\s*(.+)", text)) else ""
        audience = (
            m.group(1).strip() if (m := re.search(r"Audience:\s*(.+)", text)) else ""
        )
        location = date = start = end = ""
        if m := re.search(
            r"take place in\s+(.+?)\s+on\s+\w+,\s+(\w+ \d+, \d{4})\s*[-\u2013]\s*(\d{1,2}:\d{2})\s*to\s*(\d{1,2}:\d{2})",
            text,
        ):
            location = m.group(1)
            date = datetime.strptime(m.group(2), "%B %d, %Y").strftime("%m/%d/%Y")
            start, end = m.group(3).zfill(5), m.group(4).zfill(5)
        return replace(
            p,
            topic=topic,
            audience=audience,
            location=location,
            date=date,
            start=start,
            end=end,
        )

    with ThreadPoolExecutor(max_workers=10) as pool:
        presentations = list(pool.map(enrich, presentations))

    return presentations


def main() -> None:
    presentations = fetch_all_presentations(PRESENTATIONS_URL)
    event_count = len(presentations)

    output_file = Path(__file__).parent / "output/schedule.json"
    print(f"Saving to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(
            json.dumps(
                [presentation.__dict__ for presentation in presentations],
                indent=2,
                ensure_ascii=False,
            )
            .replace("\u2019", "'")
            .replace("\u2011", "-")
        )

    print("✓ Done!")
    print(f"  Events: {event_count}")
    print(f"  Output: {output_file}")


if __name__ == "__main__":
    main()
