import datetime as dt
import re
import unicodedata
from dataclasses import dataclass, field

MONTHS_GEN = {
    "stycznia": 1, "lutego": 2, "marca": 3, "kwietnia": 4, "maja": 5, "czerwca": 6,
    "lipca": 7, "sierpnia": 8, "września": 9, "października": 10, "listopada": 11, "grudnia": 12,
}

TURN_MD = re.compile(r"^\*\*(?P<speaker>[^*:]{1,60}):\*\*\s*(?P<text>.*)$")
TURN_PLAIN = re.compile(r"^(?P<speaker>[A-ZĄĆĘŁŃÓŚŹŻ][\wąćęłńóśźż.\- ]{0,40}):\s+(?P<text>\S.*)$")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


@dataclass
class Turn:
    index: int
    line: int
    speaker: str
    text: str


@dataclass
class Person:
    name: str
    first: str
    present: bool
    org: str | None = None
    email: str | None = None
    role: str | None = None


@dataclass
class Transcript:
    path: str
    title: str
    call_date: dt.date | None
    customer: str | None
    lines: list[str]
    turns: list[Turn]
    people: list[Person] = field(default_factory=list)

    @property
    def speakers(self) -> list[str]:
        seen = []
        for t in self.turns:
            if t.speaker not in seen:
                seen.append(t.speaker)
        return seen

    def numbered(self) -> str:
        width = len(str(len(self.lines)))
        return "\n".join(f"{i + 1:>{width}}| {line}" for i, line in enumerate(self.lines))

    def person(self, name: str | None) -> Person | None:
        if not name:
            return None
        key = fold(name.split()[0])
        for p in self.people:
            if fold(p.first) == key or fold(p.name) == fold(name):
                return p
        return None


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.replace("ł", "l").strip()


def parse_date(text: str) -> dt.date | None:
    m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", text)
    if m:
        return dt.date(int(m[1]), int(m[2]), int(m[3]))
    m = re.search(r"\b(\d{1,2})\s+(" + "|".join(MONTHS_GEN) + r")\s+(\d{4})\b", text, re.I)
    if m:
        return dt.date(int(m[3]), MONTHS_GEN[m[2].lower()], int(m[1]))
    m = re.search(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b", text)
    if m:
        return dt.date(int(m[3]), int(m[2]), int(m[1]))
    return None


def _parse_people(lines: list[str]) -> list[Person]:
    people: list[Person] = []
    section = None
    for line in lines:
        if line.startswith("## "):
            section = fold(line[3:])
            continue
        if section is None or not section.startswith("uczestnic"):
            continue
        if line.startswith("- "):
            names = BOLD.findall(line)
            if not names:
                continue
            rest = BOLD.sub("", line[2:]).strip(" ,")
            parts = [p.strip() for p in rest.split(",") if p.strip()]
            email = EMAIL.search(line)
            org = None
            role = None
            non_email = [p for p in parts if not EMAIL.fullmatch(p)]
            if len(non_email) >= 2:
                role, org = non_email[0], non_email[1]
            elif non_email:
                org = non_email[0]
            people.append(Person(names[0], names[0].split()[0], True, org, email[0] if email else None, role))
        elif "nieobecn" in fold(line) or "wspominan" in fold(line):
            for m in re.finditer(r"\*\*([^*]+)\*\*\s*(\(([^)]*)\))?", line):
                people.append(Person(m[1], m[1].split()[0].replace("pani", "").strip() or m[1], False, None, None, m[3]))
    for p in people:
        if p.name.lower().startswith("pani ") or p.name.lower().startswith("pan "):
            p.first = p.name.split()[-1]
    return people


def _customer_from_title(title: str, people: list[Person]) -> str | None:
    for sep in ("×", " x ", " X ", " - ", " vs "):
        if sep in title:
            left, right = title.split(sep, 1)
            right = right.split(":")[0]
            for side in (left, right):
                if "rinvo" not in side.lower():
                    return side.strip(" #")
    for p in people:
        if p.org and "rinvo" not in p.org.lower():
            return p.org
    return None


def load(path: str, call_date: dt.date | None = None) -> Transcript:
    raw = open(path, encoding="utf-8").read().replace("\r\n", "\n").replace("\r", "\n")
    raw = unicodedata.normalize("NFC", raw)
    lines = raw.split("\n")
    title = next((l.lstrip("# ").strip() for l in lines if l.startswith("# ")), "")
    if call_date is None:
        call_date = parse_date("\n".join(lines[:15]))
    people = _parse_people(lines)
    turns: list[Turn] = []
    start = 0
    for i, line in enumerate(lines):
        if line.startswith("#") and any(k in fold(line) for k in ("transkryp", "transcript")):
            start = i + 1
    for i in range(start, len(lines)):
        m = TURN_MD.match(lines[i]) or TURN_PLAIN.match(lines[i])
        if m:
            turns.append(Turn(len(turns), i + 1, m["speaker"].strip(), m["text"]))
    known_first = {fold(p.first) for p in people}
    for t in turns:
        if fold(t.speaker.split()[0]) not in known_first:
            people.append(Person(t.speaker, t.speaker.split()[0], True))
            known_first.add(fold(t.speaker.split()[0]))
    return Transcript(path, title, call_date, _customer_from_title(title, people), lines, turns, people)
