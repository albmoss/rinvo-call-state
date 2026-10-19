# What follows from a call

An **item** is one thing that a single owner can do, miss, or violate on their own. If two actions can fail independently (fix the address, then tell the customer it is fixed), they are two items. If one statement only restates or confirms another (the closing summary of a call), it adds evidence to the existing item and does not create a new one.

Every item has a **type** (what kind of thing it is, which decides where it goes) and a **state** (where it stands after the whole call). The two are independent: Opel enablement is a `config_change` in state `deferred`; a request to use the customer's name in a case study is a `constraint` that is `active` until an absent approver says otherwise.

## Types

| Type | Who acts | Action / destination | Cost of missing it | Cost of raising it wrongly |
|---|---|---|---|---|
| `bug` | Rinvo engineering, owned by the account manager | Ticket with the reported symptom, the configured rule it breaks, and the examples given (time, number suffix, campaign) | High. The same failure keeps hitting the customer's leads, and they told us once already | Low. An investigation ticket that closes as "works as configured" |
| `config_change` | Rinvo account manager, after human approval | Change request against this customer's agent or campaign: knowledge base, calling hours, retry rules, script, campaign launch, brand enablement | High. The customer asked for it and checks it (the address, the hours) | Very high. Changing a setting the customer did not sign off on is the most expensive error in this domain. Never executed automatically |
| `feature_request` | Rinvo product | Backlog entry, or a vote on an existing one, with the customer's words and their success measure. No date unless one was promised | Low to medium. Lost demand signal | Low internally. High if it reaches the recap as a promise |
| `commitment` | Either side, named person | Rinvo side: task with due date. Customer side: "waiting on" entry that the recap lists and a follow-up may watch | Medium to high. Missed promises are what the customer remembers | Medium. Doing unrequested work, or telling the customer they owe us something they never promised |
| `follow_up` | Rinvo, named person | Scheduled reminder with a trigger, a deadline it watches, a maximum count, and a channel. Draft only | Medium. The dependent work stalls | High. A reminder after the thing arrived, or three reminders when the customer asked for one |
| `billing` | Rinvo finance (Michał), via the account manager | Finance task: invoice correction, credit, pricing or metering question | High. Accounting cannot book the invoice; trust drops fast on money | Medium. Credits issued or promised without cause |
| `constraint` | Everyone at Rinvo, permanently or within a window | Entry in the customer's constraint registry. Every future change request, reminder, and draft is checked against it, and it is carried into the next call | Highest. Contacting someone we were told not to contact, launching during a freeze, re-running a list we were told not to re-run | Medium. We hold back something that was allowed |
| `account_signal` | Rinvo account owner | Internal alert: churn risk, competitor, decision-maker sentiment, success story. Never customer facing | High for churn signals: we lose the account without seeing it coming | Low. An alert someone reads and dismisses |

## States

| State | Meaning | Required fields |
|---|---|---|
| `open` | Someone must act, nothing blocks them | owner |
| `conditional` | The action happens only when a trigger fires or an event occurs | `condition` |
| `pending_approval` | Waiting for a decision by a named person, usually someone who was not on the call | `approvers` |
| `deferred` | Explicitly parked. Do nothing until the reopen condition holds | `condition` (reopen condition), `approvers` (who reopens it) |
| `blocked` | We want to act but lack an input (a recording, a phone number) | `condition` (what unblocks it) |
| `rejected` | Explicitly declined in the call | evidence of the refusal |
| `active` | Constraint in force, optionally within `when` | none |
| `closed` | Settled within the call, nothing left to do | none |
| `noted` | Account signal, information only | none |

## Fields

| Field | Content |
|---|---|
| `id`, `type`, `state`, `title` | as above |
| `owner` | `{party: rinvo \| customer, person}`. The person who must act. For constraints, the party bound by it |
| `action` | What the owner does, in one sentence |
| `when` | `{kind, phrase, start, end, time}`. `kind` is `by`, `on`, `not_before`, `range`, `window` or `past`. `phrase` is the verbatim words from the transcript; `start`/`end` are calendar dates resolved from the call date |
| `condition` | Trigger or reopen condition in words, plus the verbatim phrase it rests on |
| `limit` | `{max_count, channel}` for anything that contacts the customer |
| `authority_keys` | Keys into the account's authority matrix (who decides brands, cost, customer copy, case-study names, after-hours, training dates, invoicing). Approver names are resolved from the matrix, which also lists people who explicitly cannot decide |
| `value` | For changes: `{current, requested}`. The current value is what the call claims; it is checked against data when data exists |
| `evidence` | List of `{speaker, quote, line, role}`. `role` is `origin`, `revision`, `final`, `confirmation`, `condition` or `superseded`. Quotes are verbatim and verified against the transcript |
| `revised` | True when a later statement changed an earlier one. The item holds the final state; the earlier statement stays in `evidence` with role `superseded` |
| `known` | `new`, `known_previous_call`, `known_other_customers` or `known_backlog`, with the basis |
| `customer_visible` | Whether the item may appear in customer-facing drafts |
| `claims` | Factual statements about our system or data made in the call, with the data source that would confirm them |
| `ambiguities` | Places where the call itself is unclear and a human should decide |

## How the scheme covers the hard cases

- **Commitments by either side.** `commitment` with `owner.party = customer` is a first-class item. "Kasia sends the file on Monday" is tracked exactly like "Marek sends the price this week", and a `follow_up` can point at it.
- **Conditions and triggers.** `follow_up` items carry the deadline they watch (`when`), the trigger (`condition`), and the count (`limit.max_count`). "If X doesn't arrive by Monday, send one reminder" becomes `when.end = Monday`, `condition = X not received`, `max_count = 1`, `channel = email`.
- **Deferred or not approved.** State `deferred`, `pending_approval` or `rejected`, always with the reopen condition and who may reopen it. A deferred item never produces a change request or a reminder.
- **Standing prohibitions.** `constraint` items, with an optional validity window. The registry is carried into the next call and checked against every proposed action.
- **Approval by someone not on the call.** The item points to an authority-matrix entry; the state is `pending_approval` until the approver decides. If a person on the call says someone cannot approve something, that person goes into the entry's `not_authorized` list, and a request from them is flagged instead of acted on.
- **Revised statements.** One item, final state, `revised = true`, the earlier quote kept with role `superseded` and the later one with role `revision` or `final`. Both are cited.

## Annotation rules

1. One item per independently missable action or rule. The closing summary of a call is confirmation evidence.
2. Declined offers ("I can also send a sample text" / "No, just the price") are a revision of the offering item, not a separate rejected item.
3. A topic that produced a decision is one item in the state of the decision. The complaint that led to it is evidence, not a separate bug, unless the bug itself still needs work.
4. Actions internal to the customer that Rinvo neither waits for nor reports on are out of scope.
5. Data claims (numbers, current settings, timestamps) go into `claims` of the item they support. They do not become items.
6. Conditions belong to the item they gate. A time window that only gates one item ("not this week") stays in that item's condition. A window that gates everything ("nothing new during my holiday") is a constraint.

## Date conventions

The call date anchors every relative expression. For a call on Tuesday 6 October 2026:

| Expression | Resolution |
|---|---|
| `dzisiaj`, `po callu`, `po spotkaniu`, `zaraz po rozmowie` | call date |
| `wczoraj`, `w sobotę` (past tense) | the most recent such day before the call |
| `do czwartku`, `w poniedziałek` (future) | the next such day after the call date |
| `przyszły czwartek` | that weekday in the next calendar week (15 October), cross-checked against any day of month said nearby |
| `w tym tygodniu` | by Friday of the call's week |
| `w przyszłym tygodniu` | Monday to Friday of the next week |
| `w tym miesiącu` (as a block) | until the last day of the month, so `not_before` the first day of the next month |
| `od dziewiętnastego do dwudziestego trzeciego` | day numbers in the call's month, or the next month if already past |

A follow-up appears in its owner's Today view on the deadline it watches, with a ready draft, as long as the watched item has not been marked received and the follow-up has not reached its `max_count`. Nothing is scheduled or sent by the system.

## What we do not automate

- Sending anything to the customer. The recap, reminders, and status messages are drafts. A person reads and sends them.
- Executing configuration changes. The system writes a change request with the customer's verbatim approval. A person makes the change and records who approved it.
- Issuing credits or invoice corrections.
- Lifting or expiring a constraint before its stated window ends, and accepting second-hand approvals ("Kasia said it can start on Tuesday"). Only the named approver, directly, counts.
- Contacting anyone not on the call (an absent decision-maker, a salesperson the customer asked us not to contact).
- Resolving ambiguities the call itself leaves open. They are surfaced for a person to decide.

Where a human acts: one daily review (see `docs/process.md`). It holds every draft that would reach the client, every configuration change spec, every money action, quarantined items, ambiguities and constraint conflicts. Tickets, backlog entries, reminders and constraint-registry entries are filed without a click, since a wrong internal entry costs little and the review shows it anyway.
