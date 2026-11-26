<p align="center">
  <img src="assets/logo.png" alt="Telegram Reactions Sorter logo" width="96">
</p>

<h1 align="center">Telegram Reactions Sorter</h1>

<p align="center">
  Fetch, rank and visualize Telegram channel messages by reaction count.<br>
  JSON output for agents, dark-mode dashboard for humans.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&amp;logoColor=white" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT license">
  <img src="https://img.shields.io/badge/Telethon-MTProto-26A5E4?logo=telegram&amp;logoColor=white" alt="Telethon MTProto">
  <img src="https://img.shields.io/badge/Pandas-Data-150458?logo=pandas&amp;logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/Rich-CLI-blueviolet" alt="Rich CLI">
  <img src="https://img.shields.io/badge/Chart.js-Web-FF6384?logo=chartdotjs&amp;logoColor=white" alt="Chart.js">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey" alt="Windows, macOS and Linux">
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen.svg" alt="PRs welcome">
  <a href="https://github.com/zis3c/Tgreactsort/actions/workflows/tests.yml"><img src="https://github.com/zis3c/Tgreactsort/actions/workflows/tests.yml/badge.svg" alt="CI status"></a>
</p>

<p align="center">
  <img src="preview.png" alt="tgreactsort Web Dashboard Preview" width="800">
</p>

<p align="center">📺 <strong>Video Tutorial:</strong> <a href="https://youtu.be/VaF5Oofap6E"><strong>Watch how to use the repo here</strong></a></p>

A high-performance Telegram channel analytics tool built with Python and `Telethon`. Fetches messages from any channel, ranks them by total reactions, and launches a dark-mode web dashboard for deep engagement analysis.

> [!NOTE]
> **Personal Use**: This tool authenticates as a real Telegram user account. Ensure your usage complies with [Telegram's Terms of Service](https://telegram.org/tos). Only fetch data from channels you have legitimate access to.

## Features

- 🚀 **Incremental Sync**: Only fetches new messages since the last run - fast and API quota-friendly.
- 🔄 **Reaction Refresh**: Re-fetches reaction counts for existing messages without re-downloading content.
- 📚 **Smart Backfill**: Automatically fills historical gaps if the dataset is below your requested limit.
- 🗂️ **Batch Channels**: Process multiple channels in a single run with `--channels`.
- 👁️ **Watch Mode**: Loop indefinitely, auto-refreshing on a configurable timer.
- 📅 **Date Filtering**: Scope any fetch to a specific date window.
- ✏️ **Edit Detection**: Patches rows when Telegram messages are edited between runs.
- 🎨 **Modern UI**: Beautiful, color-coded CLI with `rich` progress bars, tables, and prompts.
- 🌐 **Web Dashboard**: Dark-mode viewer with charts, emoji filters, date picker, live search, bookmarks, and CSV export.

## Installation

1. **Clone the repository**
   ```bash
  git clone https://github.com/zis3c/Tgreactsort
  cd Tgreactsort
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get your API credentials**

   Go to [my.telegram.org](https://my.telegram.org) → **API development tools** → create an app. Copy your **API ID** and **API Hash**.

   Optionally, create a `.env` file:
   ```bash
   cp .env.example .env
   # Fill in API_ID and API_HASH
   ```

## Project Structure

```
tgreactsort/
├── .github/workflows/      # GitHub Actions: lint + tests matrix
├── assets/                 # Brand logo for the marketplace listing
│   ├── logo.png
│   └── logo.svg
├── SKILL.md                # Agent skill definition (Agensi / SKILL.md standard)
├── sort_reactions.py       # Main CLI - fetch, sort, and export messages
├── open_viewer.bat         # Windows shortcut to start HTTP server and open dashboard
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Test and lint dependencies
├── pytest.ini              # Test configuration
├── ruff.toml               # Lint configuration
├── tests/                  # Unit tests for CLI, helpers and skill packaging
├── .env.example            # Credentials template (copy to .env)
├── config.json             # Saved API credentials - auto-created, gitignored
├── files.json              # Registry of imported CSVs used by the web viewer
├── TOOL_DOCUMENTATION.md   # Capabilities and awareness guide
├── CONTRIBUTING.md         # Contribution guidelines
├── data/                   # Exported CSVs - one file per channel, gitignored
│   └── channel_name.csv
└── web/                    # Browser-based analytics dashboard
    ├── view_results.html   # Main dashboard page
    ├── app.js              # All frontend logic (filters, charts, search)
    └── styles.css          # Custom styles
```

## Usage

### Interactive Mode
Simply run the script without arguments:
```bash
python sort_reactions.py
```
Follow the prompts to enter your API credentials (saved for future runs) and the target channel. The web viewer launches automatically when done.

### Command Line Interface
To see all available options:
```bash
python sort_reactions.py --help
```

**Example:**
```bash
python sort_reactions.py --channel "@ExampleChannel" --limit 1000 --top 20
```

| Argument | Description | Default |
|----------|-------------|---------|
| `--channel` | Target channel username or link (`@channel`, `t.me/channel`) | - |
| `--channels` | Batch mode: multiple channels, e.g. `--channels "@a" --channels "@b"` (repeatable) | - |
| `--limit` | Number of recent messages to fetch | `1000` |
| `--top` | Number of top messages to display in terminal | `10` |
| `--json` | Headless JSON output for agents (no prompts, no browser) | `False` |
| `--start-date` | Fetch messages from this date (`YYYY-MM-DD`) | - |
| `--end-date` | Fetch messages up to this date (`YYYY-MM-DD`) | - |
| `--refresh` | Update reaction counts on existing messages only | `False` |
| `--full` | Ignore cache - full fresh fetch, overwrites CSV | `False` |
| `--watch` | Continuous refresh loop | `False` |
| `--interval` | Minutes between `--watch` refreshes | `30` |

### Agent / JSON Mode

`--json` is built for AI agents and scripts. It never prompts, never opens the dashboard and writes machine-readable JSON to stdout:

```bash
python sort_reactions.py --channel "@ExampleChannel" --limit 1000 --top 20 --json
```

The first Telegram login is still interactive (phone number and code), so the user must run the script once in their own terminal before headless runs work. Use `API_ID` and `API_HASH` environment variables or a `.env` file for credentials. See [SKILL.md](SKILL.md) for the JSON schema and agent workflow.

## How It Works

1. **Authentication**: Connects to Telegram using MTProto via your API credentials and a saved session file.
2. **Incremental Fetch**: Reads the existing CSV to find the last message ID, then only fetches newer messages.
3. **Reaction Extraction**: For each message, collects total reaction count and a per-emoji breakdown.
4. **Merge & Sort**: Merges new data with existing records, detects edits, and sorts by total reactions.
5. **Export**: Saves results to `data/<channel>.csv` and updates `files.json` for the web viewer.
6. **Web Viewer**: Launches a local HTTP server and opens the dashboard automatically in your browser.

## Testing

Install the test dependencies and run the suite from the repository root:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

The tests cover the JSON output contract, JSON error paths, batch mode, reaction label resolution, message links, record formatting and SKILL.md packaging. No Telegram account or network access is needed.

CI runs the suite on Ubuntu and Windows with Python 3.9, 3.11 and 3.13, and runs Ruff on every push and pull request.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on reporting bugs, suggesting enhancements, and submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
