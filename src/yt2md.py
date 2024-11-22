import argparse
import asyncio
import re
import ssl
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
import html

import aiohttp
import orjson
from aiohttp_socks import ProxyConnector

PROXY = "http://127.0.0.1:801"


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    for _ in range(3):
        try:
            async with session.get(url) as resp:
                return await resp.text()
        except aiohttp.ClientError:
            if _ == 2:
                raise


async def extract_metadata(content: str) -> dict:
    match = re.search(
        rb"ytInitialPlayerResponse\s*=\s*({.+?})\s*;", content.encode())
    if not match:
        raise ValueError("JSON object not found in the content.")

    json_data = orjson.loads(match.group(1))
    video_details = json_data.get("videoDetails", {})
    microformat = json_data.get("microformat", {}).get(
        "playerMicroformatRenderer", {})

    publish_date = microformat.get("publishDate", "N/A")
    if publish_date != "N/A":
        try:
            publish_date = datetime.fromisoformat(publish_date).strftime(
                "%d %B %Y y., %H:%M"
            )
        except ValueError:
            publish_date = "N/A"

    return {
        "title": video_details.get("title", "N/A"),
        "description": video_details.get("shortDescription", "N/A"),
        "views": int(video_details.get("viewCount", 0)),
        "publish_date": publish_date,
        "tags": video_details.get("keywords", []),
        "duration_seconds": int(video_details.get("lengthSeconds", 0)),
    }


async def get_subtitle_url(content: str, lang_code: str) -> str | None:
    match = re.search(
        rb"ytInitialPlayerResponse\s*=\s*({.+?})\s*;", content.encode())
    if not match:
        return None

    data = orjson.loads(match.group(1))
    captions = (
        data.get("captions", {})
        .get("playerCaptionsTracklistRenderer", {})
        .get("captionTracks", [])
    )

    selected_subtitle = next(
        (c for c in captions if c.get("languageCode") == lang_code), None
    )

    if not selected_subtitle:
        selected_subtitle = next(
            (c for c in captions if c.get("languageCode") == "en-US"), None
        )

    if not selected_subtitle:
        selected_subtitle = next(
            (c for c in captions if c.get("languageCode") == "en"), None
        )

    if not selected_subtitle:
        selected_subtitle = next(iter(captions), None)

    return selected_subtitle["baseUrl"] if selected_subtitle else None


def clean_subtitle_text(text: str) -> str:
    """Cleans up the subtitle text by decoding HTML entities."""
    return html.unescape(text)


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
            subtitles = [
                {
                    "start": float(t.get("start", 0)),
                    "duration": float(t.get("dur", 0)),
                    "text": clean_subtitle_text(
                        (t.text or "").strip()
                    ),  # Cleaned text here
                }
                for t in ET.fromstring(subtitle_content).findall(".//text")
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
        parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    return " ".join(parts) if parts else "0 minutes"


def generate_markdown(video_data: dict) -> str:
    md = [f"# {video_data['title']}\n"]
    md.append(f"https://youtube.com/watch?v={video_data['video_id']}\n")

    md.append("\n## Metadata\n")
    md.append(f"- **Views:** {video_data['views']:,}")
    md.append(f"- **Published:** {video_data['publish_date']}")

    md.append(
        f"- **Duration:** {format_duration(video_data['duration_seconds'])}")

    if video_data.get("tags"):
        md.append(f"- **Tags:** {', '.join(video_data['tags'])}")

    if video_data["description"]:
        md.append("\n## Description\n")
        md.append(video_data["description"])

    if video_data["subtitles"]:
        md.append("\n## Subtitles\n")
        for sub in video_data["subtitles"]:
            timestamp = int(sub["start"])
            link = f"https://youtu.be/{video_data['video_id']}?t={timestamp}"
            formatted_time = f"{
                int(timestamp // 60):02d}:{int(timestamp % 60):02d}"
            md.append(f"**[{formatted_time}]({link})** {sub['text']}")

    return "\n".join(md)


def copy_to_clipboard(content: str) -> None:
    try:
        process = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE)
        process.communicate(input=content.encode("utf-8"))
        print("Content copied to clipboard.")
    except FileNotFoundError:
        print("Clipboard functionality requires 'wl-copy' to be installed.")
    except ValueError as e:
        print(f"Error: {e}")


async def process_videos(
    video_ids: list[str],
    lang_code: str,
    output_file: str | None = None,
    copy: bool = False,
) -> None:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with aiohttp.ClientSession(
        connector=ProxyConnector.from_url(PROXY, ssl=ssl_context)
    ) as session:
        results = await asyncio.gather(
            *[fetch_video_data(session, video_id, lang_code) for video_id in video_ids]
        )

        markdown_content = "\n---\n".join(
            generate_markdown(result) for result in results
        )

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            print(f"Markdown saved to {output_file}")

        if copy:
            copy_to_clipboard(markdown_content)

        if not output_file and not copy:
            print(markdown_content)


def extract_video_ids(urls: list[str]) -> list[str]:
    ids = []

    for url in urls:
        match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)

        if match:
            ids.append(match.group(1))

        elif re.match(r"[a-zA-Z0-9_-]{11}$", url):
            ids.append(url)

    return ids


def main():
    parser = argparse.ArgumentParser(
        description="Convert YouTube videos to Markdown.")

    parser.add_argument("videos", nargs="+", help="YouTube video URLs or IDs.")

    parser.add_argument(
        "-o", "--output", help="Output file path for Markdown.")

    parser.add_argument(
        "-cp", "--clipboard", action="store_true", help="Copy the output to clipboard."
    )

    parser.add_argument(
        "-l",
        "--language",
        default="ru",
        help="Subtitle language code (default is 'ru').",
    )

    args = parser.parse_args()

    video_ids = extract_video_ids(args.videos)

    asyncio.run(process_videos(video_ids, args.language,
                args.output, args.clipboard))


if __name__ == "__main__":
    main()
