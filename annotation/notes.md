# Annotation notes: Grupa Auto Tama, 6 October 2026

`tama_2026-10-06.gold.json` is the reference set. I wrote it by hand from the transcript, using the rules in `docs/scheme.md`, before writing any extraction code. It has 50 items. Line numbers refer to `transcripts/tama_2026-10-06.md`.

## Judgment calls

These are the places where another annotator could reasonably disagree. They matter for the metrics because a different call here moves an item between types or states.

| Item | Decision | Alternative |
|---|---|---|
| G08 opening A/B test | One `config_change`, `conditional`. The complaint about the agent talking over the caller is evidence, since the agreed fix is the test | A separate `bug` for "no pause before disclosure" |
| G11 Opel | `config_change`, `deferred`, approver Kasia | A `constraint` ("do not enable Opel"). I chose `deferred` because the customer wants Opel eventually and has named the reopen condition |
| G13 name column | `config_change`, `conditional` | `feature_request` (columns cannot be dragged) |
| G14 validation email layout | `feature_request`, `deferred` | `config_change` if the email template is per customer |
| G28 meeting with Paweł | `commitment`, `pending_approval` (Paweł), with Kasia's relay as a separate customer commitment (G24) | `conditional` on Kasia's confirmation |
| G33 invoice correction | Owner Michał, who issues invoices; Marek's same-day handoff is part of the item | Two items: handoff (Marek, today) and correction (Michał, next week) |
| G27 and G35 | Split: telling Kasia the count is unconditional once the bug is investigated; the credit only happens if the error is ours | One billing item |
| G39 no contact with Ola | `constraint`, though only Marek said it | Not an item, since Kasia did not ask for it |
| G43 "od wtorku" | Hypothetical quote inside a prohibition. Not a date | A date for 13 October would be wrong |

## Excluded on purpose

- The advisor calling back the holiday lead (line 110). It is the dealer's internal work; Rinvo neither waits on it nor reports it. The rule we must follow (callback is a lead, G46) is kept.
- "w ustawienia agenta nie wchodź, i tak nic tam teraz nie klikamy" (line 48). Screen-share etiquette, not an action.
- Iza's callback workload (line 176). Reason for deferring after-hours, kept as context of G18.
- The 70 / 41 / 23 / 9 numbers. Data claims attached to G48, not items.

## Revisions in this call

| Item | Earlier statement | Final state |
|---|---|---|
| G06 showroom hours | Line 82: hours unchanged, Saturday until 14:00 | Line 232-236: Saturday until 15:00, both showrooms |
| G07 calling hours | Line 104: Saturday 9:00-14:00 | Line 232-234: Saturday 9:00-15:00 |
| G08 opening | Line 56: Marek shortens it himself | Line 58-60: two versions written by Kasia, she picks |
| G25 SMS | Line 194: price and a sample text | Line 196-198: price only |
| G26 address fix | Line 84: Marek sends a test recording | Line 86-88: Marek only writes that it is fixed |
| G30 training | Line 216: training requested | Line 220: cheat sheet now, training after fresh leads on Kasia's date |

G21 (Friday not promised, Monday instead) is a correction inside one sentence, so it is not marked as revised.

## Known ambiguities left for a human

- G31: Kasia's trigger is "not both versions", Marek's is "nothing arrives". They differ if exactly one version arrives.
- G11: the context section says Paweł decides on brands, yet Kasia says Paweł does not approve Opel. The safe reading is that Opel needs Kasia.
- G33: the correction date is Marek's estimate for Michał, who was not on the call.
