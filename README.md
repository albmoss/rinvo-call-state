# callstate

Turns a client status-call transcript into a client record and a daily to-do list for the Rinvo team. Claude reads the call once, and code checks every quote against the transcript and works out the dates. The system never sends anything to the client, never changes their configuration and never touches money. It writes drafts, and a person sends them.

How it works: [docs/process.md](docs/process.md)

## Demo (no API key needed)

```bash
python -m callstate transcripts/tama_2026-10-06.md --extraction tests/fixtures/tama_2026-10-06.extraction.json
python -m callstate serve --day 2026-10-08
```

Open http://127.0.0.1:8765/today. The panel is in Polish and shows Thursday 8 October, the day the one-time reminder about the opening texts is due. Click "Dostaliśmy" on Kasia's texts and the reminder disappears.

To see a request being checked against what was agreed (Paweł cannot approve Opel, Kasia has to be asked first):

```bash
python -m callstate check --day 2026-10-14 --sender Paweł --text "Paweł prosi, żeby włączyć Opla"
```

The output for this call is already in [out/grupa_auto_tama/2026-10-06/](out/grupa_auto_tama/2026-10-06/). Start with `review_2026-10-06.md` (the daily review) and `drafts/` (emails in Polish).

## Run on a new transcript

```bash
export ANTHROPIC_API_KEY=sk-ant-...        # PowerShell: $env:ANTHROPIC_API_KEY = "sk-ant-..."
python -m callstate path/to/transcript.md
```

The file needs the call date in its header and turns written as `**Name:** text`, like `transcripts/tama_2026-10-06.md`. A call costs roughly $1-1.5 with Claude Opus 5.5. That is an estimate from the size of the demo call; no live call was made.

## Requirements

Python 3.10 or newer, no packages. On Windows without time-zone data, run `pip install tzdata`. Tests: `pip install pytest`, then `python -m pytest tests`.

## Also in the repository

- `annotation/`: the hand annotation of the call and notes on changes made to it later
- `evaluation/`: precision and recall of the system against that annotation
- `docs/scheme.md`: item types, states and fields
