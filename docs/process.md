# Process: from call transcript to actions

```mermaid
flowchart TD
    T[Transcript file] --> P[Parse: speakers, turns, call date, participants, absent people]
    L[(Customer ledger:<br/>open items + constraints<br/>from earlier calls)] --> X
    B[(Product backlog)] -.production.-> D
    C[(Config export,<br/>call log, invoices)] -.production.-> K
    P --> X[Extract items with an LLM<br/>scheme prompt, verbatim quotes]
    X --> V{Validate:<br/>quotes exist verbatim<br/>for that speaker,<br/>schema, state rules}
    V -- errors --> R[One repair pass<br/>with the validator's errors] --> V
    V -- no verifiable quote --> Q[Quarantine:<br/>review queue only]
    V --> DT[Resolve dates by rule<br/>from the call date,<br/>compare with model]
    DT --> K[Check claims:<br/>calendar now,<br/>config / call log / invoice<br/>when data exists]
    K --> D[Deduplicate:<br/>within the call by quote overlap,<br/>against the ledger by id and title,<br/>against the backlog]
    D --> G[Guard: every dated action<br/>checked against active constraints]
    G --> RT{Route by type and state}

    RT -- bug, billing,<br/>Rinvo commitment --> TK[Ticket drafts]
    RT -- config_change --> CR[Change requests<br/>with customer's approving quote]
    RT -- follow_up --> RM[Reminder proposals<br/>deadline, max count, channel]
    RT -- customer visible --> EM[Recap email draft, Polish]
    RT -- account_signal,<br/>absent owner, ambiguity --> AL[Internal alerts]
    RT -- constraint --> CS[Constraint registry entries]
    RT -- feature_request --> BL[Backlog entry or vote]

    TK --> H1([Human: triage]) --> TOOLS1[Issue tracker]
    CR --> H2([Human: approve,<br/>then execute by hand]) --> TOOLS2[Agent configuration]
    RM --> H3([Human: approve schedule]) --> SCH[Scheduler] --> PC{On the day:<br/>did the awaited thing arrive?}
    PC -- yes --> CANCEL[Cancel]
    PC -- no --> SEND[Send once, count against max]
    EM --> H4([Human: edit and send]) --> MAIL[Email]
    AL --> SL[Internal channel]
    CS --> H5([Human: confirm entry]) --> L
    BL --> H6([Human: merge with existing request]) --> B
    TK & CR & RM --> LG[Write ledger for this call]
    LG --> L
    L --> NB[Next call brief:<br/>what we owe, what we wait for,<br/>what is on hold, what is forbidden]

    classDef built fill:none,stroke-width:3px
    class P,X,V,R,Q,DT,K,D,G,RT,TK,CR,RM,EM,AL,CS,LG,NB built
```

Thick borders mark what this repository builds. Dotted inputs (backlog, configuration export, call log) are wired in the design but not in the slice, because no such data was provided with this call. Everything to the right of a human step is outside the slice: the system writes drafts, never sends or changes anything.

## Where humans approve

| Step | Who | What they check |
|---|---|---|
| Change request | Account manager, then whoever executes | The customer's quote really approves this exact value; conditions hold; no active constraint blocks it |
| Recap email | Account manager | Every line was agreed; nothing internal leaks; tone |
| Reminder schedule | Account manager | Count and channel match what the customer asked for; the pre-send check is clear |
| Credit or invoice correction | Finance | The error is ours; amount |
| New constraint | Account manager | Wording and validity window, since it binds every later action |
| Quarantined item | Account manager | Whether the model invented it or misquoted a real item |

## Deduplication

- **Within the call.** A closing summary repeats earlier agreements. The prompt treats repeats as confirmation evidence, and the validator flags two items of the same type whose quotes overlap by half or more.
- **Against the previous call.** The previous ledger goes into the prompt with item ids. The model links an item with `previous_id`; the code checks that the id exists and, when no link is given, flags items whose titles resemble a previous item of the same type. Linked items replace the earlier version in the new ledger.
- **Against the backlog.** In production, feature requests are matched against the backlog before filing, so a known request gets a vote and the customer's success measure instead of a new ticket. The slice marks requests the call itself calls known ("other customers asked") as `known_other_customers`.

## Carry-over to the next call

`ledger.json` is written for every call under `out/<customer>/<date>/`. On the next run for the same customer the newest earlier ledger is loaded automatically:

1. Open, conditional, pending, deferred and blocked items are passed to the model as context and carried into the new ledger unless the new call updates or closes them.
2. Active constraints are carried until their window ends (a holiday freeze ending on 23 October is dropped from a call on 26 October) or until the named approver lifts them in a later call.
3. `next_call_brief.md` lists what Rinvo owes, what the customer owes, what is waiting for whom, and every constraint in force, so the account manager opens the next call with the state rather than with the last recap.
