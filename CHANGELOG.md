# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-06-01

### Added
- Garmin Connect MCP server with **127 tools** — 48 curated tools with friendly
  date handling, plus every remaining `garminconnect` 0.3.2 method auto-exposed
  (endurance score, intensity minutes, weekly steps/stress, FTP, lactate
  threshold, nutrition, golf, gear stats, scheduled workouts, training plans,
  badge challenges, and write/upload/delete actions). The set stays in sync with
  the library automatically.
- Native Garmin authentication with multi-factor (MFA) support via a one-time
  `garmin-mcp-server-login`; tokens are cached and auto-refreshed.
- LLM-friendly responses: large time-series are trimmed; dates accept
  `today` / `yesterday` / `-7` / ISO.
- Available on PyPI — `pip install garmin-mcp-server`.

[0.2.0]: https://github.com/stitrace/garmin-mcp-server/releases/tag/v0.2.0
