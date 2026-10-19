# callstate: account assistant built from client call transcripts

After a status call with a dealer, someone at Rinvo has to work out what was agreed, what is on hold, what to remind the client about, who approves what, and what to prepare. This tool does that from the transcript file alone.
One Claude call per transcript extracts the client record (people, who decides what, current facts) and every item with verbatim quotes; code checks each quote against its line and speaker, resolves relative dates from the call date, and stores everything in SQLite.
The result is a shared client view, a "Today" list per person, reminders that appear only if the awaited thing has not arrived, Polish drafts, change specs, dev tickets and briefs.
It never sends anything to the client, never changes the client's configuration and never touches money: those come out as drafts for one daily review.
A later transcript for the same client updates the record: superseded values are kept and linked, closed items close, conflicts with earlier agreements are flagged.

How it works, on one page: [docs/process.md](docs/process.md).

## Demo in 3 commands (no API key needed)

The demo replays the model response saved in `tests/fixtures/` instead of calling the API.

```bash
python -m callstate transcripts/tama_2026-10-06.md --extraction tests/fixtures/tama_2026-10-06.extraction.json
python -m callstate serve --day 2026-10-08
python -m callstate check --day 2026-10-14 --sender Paweł --text "Paweł prosi, żeby włączyć Opla"
```

1. Ingests the call into `callstate.db` and writes `out/grupa_auto_tama/2026-10-06/`.
2. Opens the panel at http://127.0.0.1:8765/today as of Thursday 8 October, the day the one-time reminder about the opening texts is due. Tabs: Today, Client, Waiting on client, Drafts, Daily review. The buttons record events (received, sent, done); mark the texts as received and the reminder disappears.
3. Shows that Paweł cannot approve Opel and that Kasia must be called first. The same check is on the Client tab.

Optional: process a second call. `tests/fixtures/synthetic_followup_2026-10-13.md` is a short follow-up call written for this demo (it is not from Rinvo); its saved extraction updates the record from the first call.

```bash
python -m callstate tests/fixtures/synthetic_followup_2026-10-13.md --extraction tests/fixtures/synthetic_followup_2026-10-13.extraction.json
python -m callstate serve --day 2026-10-13
```

### What to look at in `out/grupa_auto_tama/2026-10-06/`

| File | Content |
|---|---|
| `review_2026-10-06.md` | The daily review: drafts ready to send, items due per person, quarantine, ambiguities, constraint conflicts |
| `drafts/recap_email_pl.md`, `drafts/messages_pl.md` | Polish recap email to the client, reminders, handoff to Michał, invitation to Paweł |
| `change_specs.md` | Exact configuration changes for a person to apply, with status and earliest start date |
| `dev_tickets.md`, `backlog.md` | Bugs with the evidence from the call; product requests with the client's success metric and "no deadline promised" |
| `meeting_brief_I42.md`, `next_call_brief.md` | Brief for the meeting with Paweł; pre-call brief for the next call with Kasia |
| `client.md`, `ledger.json`, `items.json` | The shared client record and the full item list with quotes and line numbers |

## Running on a new transcript

Set the key in the environment; it is read from nowhere else.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export CALLSTATE_MODEL=claude-opus-5-5   # optional, this is the default
python -m callstate path/to/transcript.md
```

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
$env:CALLSTATE_MODEL = "claude-opus-5-5"   # optional
python -m callstate path\to\transcript.md
```

The transcript is a Markdown file like `transcripts/tama_2026-10-06.md`: a header with the call date, a participant list, and turns written as `**Name:** text`. If the header has no date, pass `--date YYYY-MM-DD`. A transcript for a client already in `callstate.db` is processed against that client's record. `ANTHROPIC_BASE_URL` overrides the API host (default `https://api.anthropic.com`).

If the response does not match the schema, the tool asks the model once to repair it and then fails with the list of errors, ingesting nothing. Items whose quotes are not found on the cited line for the cited speaker are quarantined and shown in the daily review.

Cost, estimated from the size of the demo call (no live call was made): about 20k input tokens and 50-60k output tokens with Claude Opus 5.5 at $4 / $20 per million tokens, so roughly $1-1.5 per call, up to double if the repair pass runs.

## Requirements

- Python 3.10 or newer (developed on 3.12). No packages are needed to run it.
- Windows: the panel's default "today" uses the Europe/Warsaw time zone. If Python has no time-zone data, run `pip install tzdata`, or pass `--day`.
- Tests: `pip install pytest`, then `python -m pytest tests`.

## Also in the repository

- `annotation/`: the hand annotation of the 6 October call (50 items plus the account section) and notes on judgment calls and later changes.
- `evaluation/`: precision and recall against the annotation, strict and tolerant (`metrics.md`), and the scenario test log (`test_results.txt`). Score a run with `python -m callstate eval annotation/tama_2026-10-06.gold.json out/grupa_auto_tama/2026-10-06/items.json --out evaluation`.
- `docs/scheme.md`: item types, states and fields.
