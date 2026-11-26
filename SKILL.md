---
name: telegram-reactions-sorter
description: Fetch, rank and export Telegram channel messages by total reactions, views, forwards and engagement velocity. Use when the user asks to analyze a Telegram channel, find top posts by reactions, sort messages by engagement, compare multiple channels, or export Telegram channel analytics.
---

# Telegram Reactions Sorter

Fetch messages from one or more Telegram channels with Telethon, rank them by total reactions, and return the top posts with reaction breakdowns, views, forwards, engagement velocity and direct links.

Runs entirely on the user's machine with the user's own Telegram account. No third-party API keys or hosted services are used.

## Requirements

- Python 3.9 or newer.
- A Telegram account plus an API ID and API hash from https://my.telegram.org (API development tools).
- Access to any private channel being analyzed. Public channels work by username or link.

## Setup once per machine

Work from this skill's root directory (the folder containing `SKILL.md`).

1. Install dependencies:

   ```
   python -m pip install -r requirements.txt
   ```

2. Ask the user for their Telegram API ID and API hash. Have them put the values in environment variables `API_ID` and `API_HASH`, or in a `.env` file in the skill root:

   ```
   API_ID=123456
   API_HASH=your_api_hash_here
   ```

3. The first Telegram login is interactive: Telethon asks for a phone number and a login code. The user must run this once in their own terminal, not through an agent tool call that cannot accept interactive input:

   ```
   python sort_reactions.py --channel "@durov" --limit 50
   ```

   This saves `session_name.session` and `config.json` in the skill root for future runs.

4. Verify the session works headlessly with the JSON command in the next section.

Never ask the user to paste their login code, session file or API hash into chat. Never commit or share `session_name.session` or `config.json`.

## Analyze a channel

From the skill root:

```
python sort_reactions.py --channel "@channelname" --limit 1000 --top 20 --json
```

Key options:

| Option | Meaning |
| --- | --- |
| `--channel` | One channel username, link or ID. |
| `--channels` | Repeat for batch mode: `--channels "@a" --channels "@b"`. |
| `--limit` | How many recent messages to scan (default 1000). |
| `--top` | How many top messages to return (default 10). |
| `--start-date`, `--end-date` | Date window in `YYYY-MM-DD`. |
| `--refresh` | Update reaction counts for messages already saved. |
| `--full` | Ignore cached CSV data and fetch fresh. |
| `--json` | Headless mode for agents: no prompts, no browser, JSON on stdout. |

Date filters apply during the fetch. If the channel already has cached data, add `--full` to limit the dataset cleanly to the window (this overwrites that channel's CSV).

`--json` behavior:

- Requires `--channel` or `--channels`.
- Requires an existing authorized session and credentials from the environment, `.env` or `config.json`.
- Writes only JSON to stdout; progress and logs are suppressed. Errors are JSON on stdout with exit code 1.
- Always saves the CSV under `data/` and never opens the dashboard or a browser.
- `--watch` is not supported with `--json`.

Successful output shape:

```json
{
  "ok": true,
  "results": [
    {
      "ok": true,
      "channel": "@channelname",
      "total": 1000,
      "csv": "data/channelname.csv",
      "top": [
        {
          "id": 123,
          "date": "2025-01-01 10:00:00+00:00",
          "total_reactions": 420,
          "breakdown": "👍: 300, 🔥: 120",
          "views": 12000,
          "forwards": 33,
          "velocity": 2.1,
          "text": "full message text",
          "link": "https://t.me/channelname/123"
        }
      ]
    }
  ]
}
```

`velocity` is reactions per hour since the message was posted. `breakdown` is the per-emoji reaction string. `total` is the number of messages in the dataset, not only the returned top list.

If a channel fails, its result has `"ok": false` and an `"error"` string. Check the top-level `ok` and each result's `ok` before reporting success.

## Presenting results

- Lead with a markdown table of the top 5 to 10 messages: rank, total reactions, date, short preview and link.
- Follow with a short takeaway about the themes, formats or posting patterns that earned the most reactions, and call out the highest-velocity posts.
- Link every message. Keep previews short and quote only small excerpts.
- Use the user's language and units.
- If `ok` is false, explain the error and the setup step that fixes it. Do not retry in a loop or invent data.

## Optional web dashboard

Without `--json`, the script saves the CSV and can open a dark-mode dashboard at `http://localhost:8000/web/view_results.html` with charts, filters, search, bookmarks and CSV export. Use it only when the user explicitly wants a visual dashboard; agent answers do not need it.

```
python sort_reactions.py --channel "@channelname" --limit 1000
```

The dashboard needs a browser and a local HTTP server, so it is not suitable for headless agent runs. It loads Tailwind, Chart.js, PapaParse and Google Fonts from public CDNs; the core CLI and JSON mode do not.

## Rules

- Use only the user's own Telegram credentials and account. Do not scrape with credentials the user does not own.
- Only access channels the user's account can already access.
- Respect Telegram rate limits. On FloodWait, stop and tell the user how many seconds to wait.
- Data stays local under `data/`. Do not upload it or send it to third parties.
- Do not use this skill to harass, dox or mass-message users.

## Files

- `SKILL.md` - this skill.
- `sort_reactions.py` - main CLI (fetch, rank, export, JSON output).
- `requirements.txt` - Python dependencies.
- `.env.example` - credential template.
- `web/` - optional dashboard files.
- `tests/` - unit tests (development only).
- `requirements-dev.txt`, `pytest.ini` - test setup (development only).
- `README.md` - human-oriented setup guide.
- `LICENSE` - MIT license.
