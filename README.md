# yt2md

`yt2md` is a command-line tool designed to convert YouTube videos into Markdown format. This tool extracts metadata and subtitles from YouTube videos, providing a structured output that is easy to read and use.

## Features

- **Extract Metadata**: Retrieves video title, description, view count, publish date, tags, and duration.
- **Subtitle Support**: Fetches subtitles in multiple languages based on user preference.
- **Markdown Conversion**: Outputs all extracted data in a well-structured Markdown file.
- **Clipboard Functionality**: Optionally copies the output directly to your clipboard.
- **Custom Language Selection**: Allows users to specify subtitle language with fallback options.

## Requirements

- Python 3.12 or higher
- `aiohttp`
- `orjson`
- `aiohttp_socks`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/xpos587/yt2md.git
   cd yt2md
   ```

2. Install using pip:
   ```bash
   pip install aiohttp orjson aiohttp_socks
   ```

3. Alternatively, you can run the installation script:
   ```bash
   python install.py
   ```

The script will:
- Install the package in your Python environment.
- Create a symlink in `/usr/local/bin` for global access (requires sudo).

## Usage

Basic usage:
```bash
yt2md <video_url_or_id> [options]
```

### Options:

```
positional arguments:
  video_url_or_id        YouTube video URLs or IDs.

optional arguments:
  -h, --help              Show this help message and exit
  -o, --output            Output file path for Markdown.
  -cp, --clipboard        Copy the output to clipboard.
  -l, --language          Subtitle language code (default is 'ru').
```

### Examples

1. Generate Markdown for a specific video:
   ```bash
   yt2md HNXcsxO3B94 -o output.md
   ```

2. Specify a subtitle language:
   ```bash
   yt2md HNXcsxO3B94 -o output.md -l en-US
   ```

3. Copy output directly to clipboard:
   ```bash
   yt2md HNXcsxO3B94 -cp
   ```

4. Generate Markdown without specifying an output file (prints to console):
   ```bash
   yt2md HNXcsxO3B94
   ```

## Development

To set up the development environment:

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies manually as mentioned above.

3. Install in editable mode if you make changes:
   ```bash
   pip install -e .
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add some amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

## Authors

- Michael (x30827pos@gmail.com)

## Acknowledgments

- Thanks to the `aiohttp`, `orjson`, and `aiohttp_socks` libraries for their support in building this tool.
