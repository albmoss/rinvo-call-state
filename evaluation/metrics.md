# Metrics

Gold: `annotation/tama_2026-10-06.gold.json`  
Prediction: `out/grupa_auto_tama/2026-10-06/items.json` (0 quarantined items excluded)

Found = cites overlapping transcript spans and has the gold type (strict) or a type listed as an acceptable alternative in `annotation/notes.md` (tolerant). State-correct additionally requires state, owner, date, condition presence, approvers and reminder count to match.

| Type | Gold | Pred | Strict P | Strict R | Tolerant P | Tolerant R | via alt type | State-correct strict P / R | State-correct tolerant P / R |
|---|---|---|---|---|---|---|---|---|---|
| bug | 4 | 4 | 1.00 | 1.00 | 1.00 | 1.00 | 0 | 1.00 / 1.00 | 1.00 / 1.00 |
| config_change | 9 | 12 | 0.75 | 1.00 | 0.90 | 1.00 | 0 | 0.50 / 0.67 | 0.60 / 0.67 |
| feature_request | 6 | 4 | 1.00 | 0.67 | 1.00 | 1.00 | 2 | 1.00 / 0.67 | 0.83 / 0.83 |
| commitment | 11 | 12 | 0.92 | 1.00 | 0.92 | 1.00 | 0 | 0.83 / 0.91 | 0.83 / 0.91 |
| follow_up | 2 | 2 | 1.00 | 1.00 | 1.00 | 1.00 | 0 | 1.00 / 1.00 | 1.00 / 1.00 |
| billing | 3 | 3 | 1.00 | 1.00 | 1.00 | 1.00 | 0 | 0.67 / 0.67 | 0.67 / 0.67 |
| constraint | 11 | 11 | 0.91 | 0.91 | 0.91 | 0.91 | 0 | 0.64 / 0.64 | 0.64 / 0.64 |
| account_signal | 4 | 3 | 1.00 | 0.75 | 1.00 | 0.75 | 0 | 1.00 / 0.75 | 1.00 / 0.75 |
| all | 50 | 51 | 0.90 | 0.92 | 0.94 | 0.96 | 2 | 0.75 / 0.76 | 0.76 / 0.78 |

| Field (tolerant matches) | Correct |
|---|---|
| state | 48/48 |
| owner | 48/48 |
| date | 46/48 |
| condition | 47/48 |
| approvers | 41/48 |
| limit | 48/48 |
| revised | 48/48 |
| known | 46/48 |

## Errors

- missed [G50] Recordings are worse than the dashboard suggests.
- invented [2026-10-06/I18] Paweł nie zatwierdza Opla ani tekstu wstępu.
- invented [2026-10-06/I43] Zapytać Pawła o nazwę firmy w przykładzie 208.
- wrong_approvers [G09 / 2026-10-06/I21] Launch the fresh-leads campaign when the file arrives. expected ['Kasia'], got []
- wrong_approvers [G12 / 2026-10-06/I37] SMS after two failed call attempts. expected ['Paweł'], got ['Kasia', 'Paweł']
- wrong_approvers [G43 / 2026-10-06/I35] Second-hand go-aheads for after-hours are not valid. expected ['Kasia'], got []
- wrong_approvers [G44 / 2026-10-06/I38] Kasia writes customer-facing copy; Rinvo does not. expected ['Kasia'], got []
- wrong_condition [G45 / 2026-10-06/I44] Case study only without the company name until Paweł approves. expected 'Paweł approves using the company name.', got None
- wrong_approvers [G45 / 2026-10-06/I44] Case study only without the company name until Paweł approves. expected ['Paweł'], got []
- wrong_date [G33 / 2026-10-06/I14] September invoice issued to the wrong legal entity. expected {'kind': 'window', 'start': '2026-10-12', 'end': '2026-10-16'}, got {'kind': 'by', 'start': None, 'end': '2026-10-16'}
- wrong_approvers [G28 / 2026-10-06/I42] Meeting with Paweł on Thursday 15 October, 10:00. expected ['Paweł'], got []
- alt_type [G18 / 2026-10-06/I32] After-hours inbound agent. expected 'feature_request', got 'config_change'
- wrong_known [G18 / 2026-10-06/I32] After-hours inbound agent. expected 'known_previous_call', got 'new'
- alt_type [G14 / 2026-10-06/I26] Validation email: model and showroom at the top. expected 'feature_request', got 'config_change'
- wrong_date [G14 / 2026-10-06/I26] Validation email: model and showroom at the top. expected None, got {'kind': 'not_before', 'start': '2026-10-12', 'end': None}
- wrong_type [G36 / 2026-10-06/I10] Retry limit stays at five attempts. expected 'constraint', got 'config_change'
- wrong_state [G36 / 2026-10-06/I10] Retry limit stays at five attempts. expected 'active', got 'rejected'
- wrong_known [G36 / 2026-10-06/I10] Retry limit stays at five attempts. expected 'known_previous_call', got 'new'
- wrong_approvers [G08 / 2026-10-06/I01] Manual A/B test of two opening scripts. expected ['Kasia'], got []
- wrong_known [G01 / 2026-10-06/I09] Same-day retry after a hang-up within 3 seconds. expected 'new', got 'known_previous_call'

## Matches

- G03 ↔ 2026-10-06/I05 (1.0): Agent stopped responding and asked about the model twice / Agent drugi raz pyta o model
- G09 ↔ 2026-10-06/I21 (1.0): Launch the fresh-leads campaign when the file arrives / Start walidacji świeżych leadów
- G12 ↔ 2026-10-06/I37 (1.0): SMS after two failed call attempts / SMS po dwóch nieudanych próbach połączenia
- G16 ↔ 2026-10-06/I29 (1.0): Dashboard tile click-through to the matching contacts / Kliknięcie w kafelek przenosi do listy kontaktów
- G19 ↔ 2026-10-06/I40 (1.0): Integration with the dealer's CRM / Integracja z systemem (CRM) dealera
- G21 ↔ 2026-10-06/I19 (1.0): Kasia sends the fresh-leads file / Kasia przysyła plik ze świeżymi leadami
- G23 ↔ 2026-10-06/I33 (1.0): Kasia sends assistance numbers and the field list (not a go-ahead) / Kasia przysyła numery assistance i listę pól
- G24 ↔ 2026-10-06/I41 (1.0): Kasia passes the meeting proposal to Paweł and confirms / Kasia przekazuje Pawłowi propozycję spotkania i potwierdza
- G25 ↔ 2026-10-06/I36 (1.0): Marek sends the SMS price / Cena SMS-ów dla Kasi
- G26 ↔ 2026-10-06/I07 (1.0): Marek tells Kasia when the knowledge base is fixed / Informacja dla Kasi, że adres jest poprawiony
- G27 ↔ 2026-10-06/I11 (1.0): Marek reports the number of duplicate calls with the bug outcome / Liczba podwójnych połączeń dla Kasi
- G29 ↔ 2026-10-06/I48 (1.0): Marek sends a one-page cheat sheet of lead statuses / Ściąga ze statusami dla handlowców
- G31 ↔ 2026-10-06/I03 (1.0): One reminder if the opening texts have not arrived by Thursday / Jedno przypomnienie o tekstach wstępu
- G32 ↔ 2026-10-06/I20 (1.0): One email if the fresh-leads file has not arrived on Monday / Jeden mail, jeśli pliku nie będzie w poniedziałek
- G34 ↔ 2026-10-06/I12 (1.0): Check how calls under 3 seconds are metered / Sprawdzenie naliczania minut przy krótkich połączeniach
- G37 ↔ 2026-10-06/I22 (1.0): Do not send Kasia a file template / Nie wysyłać wzoru pliku
- G38 ↔ 2026-10-06/I23 (1.0): Do not call the old lead list again / Nie puszczać drugi raz starej bazy
- G39 ↔ 2026-10-06/I27 (1.0): No direct contact with Ola; everything goes through Kasia / Nie pisać do Oli, wszystko przez Kasię
- G42 ↔ 2026-10-06/I34 (1.0): Hold after-hours materials; do not connect them / Nie podpinać numerów assistance ani listy pól
- G43 ↔ 2026-10-06/I35 (1.0): Second-hand go-aheads for after-hours are not valid / Nie wierzyć przekazom z drugiej ręki o starcie po godzinach
- G44 ↔ 2026-10-06/I38 (1.0): Kasia writes customer-facing copy; Rinvo does not / Teksty dla klientów pisze Kasia
- G45 ↔ 2026-10-06/I44 (1.0): Case study only without the company name until Paweł approves / Przykład 208 tylko bez nazwiska i nazwy firmy
- G46 ↔ 2026-10-06/I47 (1.0): A callback request is a lead, not a refusal / „Oddzwońcie po urlopie” to lead, nie odmowa
- G48 ↔ 2026-10-06/I46 (1.0): Paweł wanted to switch the service off after 9 of 70 / Ryzyko: Paweł patrzy na liczby i chciał wszystko wyłączyć
- G11 ↔ 2026-10-06/I17 (0.997): Opel stays off / Włączenie Opla wstrzymane
- G15 ↔ 2026-10-06/I04 (0.996): Self-service A/B tests in the panel / Wbudowane testy A/B w panelu
- G13 ↔ 2026-10-06/I30 (0.996): Contact list: name column right after status / Nazwisko zaraz po statusie na liście kontaktów
- G47 ↔ 2026-10-06/I39 (0.996): Competitor VoiceDesk pitched Paweł / Konkurent VoiceDesk u Pawła
- G33 ↔ 2026-10-06/I14 (0.996): September invoice issued to the wrong legal entity / Korekta faktury za wrzesień na właściwą spółkę
- G49 ↔ 2026-10-06/I45 (0.995): Success: Peugeot 208 sold after a bot call / Sukces: sprzedaż Peugeota 208 po rozmowie z botem
- G30 ↔ 2026-10-06/I49 (0.994): 15-minute status training for salespeople / Krótkie szkolenie online dla handlowców
- G28 ↔ 2026-10-06/I42 (0.994): Meeting with Paweł on Thursday 15 October, 10:00 / Zaproszenie Pawła na spotkanie
- G02 ↔ 2026-10-06/I28 (0.994): Status filter "zainteresowany" does not narrow the contact list / Filtr statusu „zainteresowany” nie zawęża listy
- G17 ↔ 2026-10-06/I31 (0.991): Weekly email report to Paweł / Cotygodniowy raport mailowy do Pawła
- G35 ↔ 2026-10-06/I13 (0.989): Credit the duplicate calls if they were our error / Odjęcie podwójnych połączeń z rozliczenia, jeśli to błąd Rinvo
- G41 ↔ 2026-10-06/I51 (0.979): Freeze during Kasia's holiday, 19-23 October / Urlop Kasi: nic nowego nie startuje
- G06 ↔ 2026-10-06/I08 (0.943): Knowledge base: Saturday showroom hours 9:00-15:00 for both showrooms / Sobotnie godziny salonów w bazie wiedzy do 15:00
- G18 ↔ 2026-10-06/I32 (1.0): After-hours inbound agent / Agent po godzinach
- G40 ↔ 2026-10-06/I50 (0.822): The agent does not sell / Agent nie sprzedaje i nie proponuje aut używanych
- G14 ↔ 2026-10-06/I26 (0.91): Validation email: model and showroom at the top / Model i salon na górze maila do handlowców
- G07 ↔ 2026-10-06/I15 (0.787): Calling hours: weekdays 9:00-19:00, Saturday 9:00-15:00, no Sunday / Skrócenie okna dzwonienia
- G05 ↔ 2026-10-06/I06 (0.755): Knowledge base: Włocławek showroom address / Poprawa adresu salonu we Włocławku w bazie wiedzy
- G36 ↔ 2026-10-06/I10 (1.0): Retry limit stays at five attempts / Obniżenie limitu prób z 5 do 3 (odrzucone)
- G04 ↔ 2026-10-06/I25 (0.747): Service request (inspection) delivered to the dealer as a sales lead / Rozmowa o przeglądzie oznaczona jako lead sprzedażowy
- G10 ↔ 2026-10-06/I16 (0.733): Move the first call attempt to lunchtime / Przesunięcie pierwszej próby na przerwę obiadową
- G08 ↔ 2026-10-06/I01 (0.729): Manual A/B test of two opening scripts / Test wstępu rozmowy w dwóch wersjach
- G01 ↔ 2026-10-06/I09 (0.725): Same-day retry after a hang-up within 3 seconds / Drugi telefon tego samego dnia po rozłączeniu w ciągu 3 sekund
- G20 ↔ 2026-10-06/I02 (0.683): Kasia writes and sends both opening texts / Kasia przysyła obie wersje tekstu wstępu
- G22 ↔ 2026-10-06/I24 (0.328): Kasia forwards Ola's misrouted service case if Ola finds it / Kasia przesyła sprawę przeglądu od Oli
