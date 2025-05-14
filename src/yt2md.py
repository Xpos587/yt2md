import argparse
import asyncio
import re
import os
import ssl
import xml.etree.ElementTree as ET
from datetime import datetime
import html

import aiohttp_socks
import aiohttp
import json


def get_system_proxy():
    """
    Creates configuration for working with system proxies through environment variables.
    Returns connector and parameters for the session.
    """
    http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    if http_proxy or https_proxy:
        proxy_url = https_proxy or http_proxy
        return aiohttp_socks.ProxyConnector.from_url(str(proxy_url), ssl=ssl_context)

    return aiohttp.TCPConnector(ssl=ssl_context)


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    for _ in range(3):
        try:
            async with session.get(url) as resp:
                return await resp.text()
        except aiohttp.ClientError:
            if _ == 2:
                raise
    return ""  # This should never be reached but satisfies the return type


async def extract_metadata(content: str) -> dict:
    match = re.search(rb"ytInitialPlayerResponse\s*=\s*({.+?})\s*;", content.encode())
    if not match:
        raise ValueError("JSON object not found in the content.")

    json_data = json.loads(match.group(1))
    video_details = json_data.get("videoDetails", {})
    microformat = json_data.get("microformat", {}).get("playerMicroformatRenderer", {})

    publish_date = microformat.get("publishDate", "N/A")
    if publish_date != "N/A":
        try:
            publish_date = datetime.fromisoformat(publish_date).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
        except ValueError:
            publish_date = "N/A"

    return {
        "title": video_details.get("title", "N/A"),
        "author": video_details.get("author", "N/A"),
        "description": video_details.get("shortDescription", "N/A"),
        "views": int(video_details.get("viewCount", 0)),
        "publish_date": publish_date,
        "tags": video_details.get("keywords", []),
        "duration_seconds": int(video_details.get("lengthSeconds", 0)),
        "channel": video_details.get("author", "N/A"),
    }


async def get_subtitle_url(content: str, lang_code: str) -> str | None:
    match = re.search(rb"ytInitialPlayerResponse\s*=\s*({.+?})\s*;", content.encode())
    if not match:
        return None

    data = json.loads(match.group(1))
    captions = (
        data.get("captions", {})
        .get("playerCaptionsTracklistRenderer", {})
        .get("captionTracks", [])
    )

    if captions:
        available_langs = [
            (c.get("languageCode"), c.get("name", {}).get("simpleText"))
            for c in captions
        ]
        print("Available subtitle languages:")
        for code, name in available_langs:
            print(f"  - {code}: {name}")

    lang_codes = [lang_code, f"{lang_code}-US", "en", "en-US"]
    for code in lang_codes:
        track = next((c for c in captions if c.get("languageCode") == code), None)
        if track:
            return track["baseUrl"]
    return captions[0]["baseUrl"] if captions else None


def clean_subtitle_text(text: str) -> str:
    return html.unescape(text).replace("\n", " ")


async def fetch_video_data(
    session: aiohttp.ClientSession, video_id: str, lang_code: str
) -> dict:
    page_url = f"https://www.youtube.com/watch?v={video_id}"
    page_content = await fetch(session, page_url)

    metadata = await extract_metadata(page_content)
    subtitle_url = await get_subtitle_url(page_content, lang_code)

    subtitles = []
    if subtitle_url:
        subtitle_content = await fetch(session, subtitle_url)
        try:
            root = ET.fromstring(subtitle_content)
            subtitles = [
                {
                    "start": float(text.get("start", 0)),
                    "text": clean_subtitle_text((text.text or "").strip()),
                }
                for text in root.findall(".//text")
            ]
        except ET.ParseError:
            subtitles = []

    metadata["video_id"] = video_id
    metadata["subtitles"] = subtitles
    return metadata


def format_duration(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    return " ".join(parts) if parts else "0m"


def format_time(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def generate_markdown(video_data: dict) -> str:
    md = []

    # Frontmatter
    md.append("---")
    md.append(f"url: https://youtu.be/{video_data['video_id']}")
    md.append(f"title: {video_data['title']}")
    md.append(f"channel: {video_data['channel']}")
    md.append(f"views: {video_data['views']:,}")
    md.append(f"duration: {format_duration(video_data['duration_seconds'])}")
    md.append(f"published: {video_data['publish_date']}")
    if video_data["tags"]:
        md.append(f"tags: [{', '.join(video_data['tags'])}]")
    md.append("---\n")

    # Main content
    md.append(f"# {video_data['title']}\n")
    md.append(f"**Channel:** [[{video_data['channel']}]]\n")
    md.append(f"**Published:** `{video_data['publish_date']}`\n")
    md.append(f"**Duration:** {format_duration(video_data['duration_seconds'])}\n")
    md.append(f"**Views:** {video_data['views']:,}\n")

    if video_data["description"]:
        md.append("\n## Description\n")
        md.append(f"{video_data['description']}\n")

    if video_data["subtitles"]:
        md.append("\n## Subtitles\n")
        for sub in video_data["subtitles"]:
            timestamp = int(sub["start"])
            link = f"https://youtu.be/{video_data['video_id']}?t={timestamp}"
            md.append(f"[{format_time(sub['start'])}]({link}) {sub['text']}")

    return "\n".join(md)


async def process_videos(
    video_ids: list[str],
    lang_code: str,
    output_file: str | None = None,
) -> None:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connector = get_system_proxy()
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            fetch_video_data(session, video_id, lang_code) for video_id in video_ids
        ]
        results = await asyncio.gather(*tasks)

        markdown_content = "\n---\n".join(
            generate_markdown(result) for result in results
        )

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            print(f"Markdown saved to {output_file}")

        if not output_file:
            print(markdown_content)


def main():
    parser = argparse.ArgumentParser(
        description="Convert YouTube videos to Obsidian-style Markdown."
    )
    parser.add_argument("videos", nargs="+", help="YouTube video URLs or IDs.")
    parser.add_argument("-O", "--output", help="Output file path for Markdown.")
    parser.add_argument(
        "-L", "--language", default="en", help="Subtitle language code (default: 'en')."
    )
    args = parser.parse_args()
    video_ids = re.findall(r"(?:v=|youtu\.be\/)([\w-]{11})", " ".join(args.videos))
    asyncio.run(process_videos(video_ids, args.language, args.output))


if __name__ == "__main__":
    main()
