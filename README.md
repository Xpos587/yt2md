# 🎬 yt2md

![PyPI](https://img.shields.io/pypi/v/yt2md)
![Python Version](https://img.shields.io/pypi/pyversions/yt2md)
![License](https://img.shields.io/github/license/xpos587/yt2md)

🚀 YouTube to Obsidian Markdown converter with metadata extraction and timestamped subtitles.

---

## ✨ Features

- **Smart Metadata Extraction**: Title, author, views, publish date, duration, tags
- **Multi-language Subtitles**: Automatic fallback (en/US → user-specified → first available)
- **Obsidian Integration**: Frontmatter with video details and wiki-style links
- **Async Architecture**: Parallel processing of multiple videos
- **Proxy Support**: SOCKS/HTTP proxies via environment variables
- **Subtitle Processing**: XML parsing with HTML entity decoding
- **Timecode Links**: Clickable timestamps linking to exact video moments

---

## 📦 Installation

```
pipx install yt2md
```

---

## 🚀 Usage

### Basic Conversion

```
yt2md VIDEO_URL or VIDEO_ID -O output.md
```

### Multiple Videos + Russian Subtitles

```
yt2md ID1 ID2 ID3 -L ru -O vault/notes.md
```

### Clipboard Integration

```
# Linux (Wayland)
yt2md ID | wl-copy

# Linux (X11)
yt2md ID | xclip -selection clipboard

# macOS
yt2md ID | pbcopy

# Windows
yt2md ID | idk?
```

---

## 🔧 Proxy Configuration

### Set Environment Variables

```
export HTTP_PROXY="socks5://localhost:9050"
export HTTPS_PROXY="$HTTP_PROXY"
```

### Usage with Proxy

```
yt2md VIDEO_ID --language en --output research.md
```

---

## 📝 Example Output

```
---
url: https://youtu.be/abc123
title: "Advanced Python Techniques"
channel: PyMaster
views: 123,456
duration: 15m 30s
published: 2024-03-15T09:30:00Z
tags: [python, programming, tutorial]
---

# Advanced Python Techniques

**Channel:** [[PyMaster]]
**Published:** `2024-03-15T09:30:00Z`
**Duration:** 15m 30s
**Views:** 123,456

## Description
Explore advanced Python features...

## Subtitles
[00:01:23] Welcome to the tutorial
[00:05:45] Context managers deep dive
[00:10:12] Metaclass examples
```

---

## ⚙️ Technical Details

### Metadata Extraction

- Parses `ytInitialPlayerResponse` JSON blob
- Handles ISO 8601 dates and view count formatting
- Fallback values for missing fields

### Subtitle System

1. Language priority: `specified → lang-US → en → en-US → first available`
2. XML parsing with error handling
3. Automatic text cleaning (HTML entities, newlines)

### Performance

- Async HTTP client with 3 retry attempts
- Parallel video processing
- Lightweight XML parser (lxml)

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

👤 Author: Michael (@xpos587)  
📧 Contact: x30827pos@gmail.com
🐛 Issues: https://github.com/xpos587/yt2md/issues
