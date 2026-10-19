# Client: grupa_auto_tama

## People

- Iza (customer, recepcja, not on the call)
- Kasia Malinowska (customer, BDC, główny kontakt klienta; decyduje o tekstach, Oplu, po godzinach i terminach, on the call, kasia.malinowska@autotama.pl)
- Ola (customer, handlowiec, not on the call)
- Paweł (customer, przełożony Kasi; decyduje o budżecie, kosztach, nazwie firmy w przykładach; kontakt awaryjny w czasie urlopu Kasi, not on the call)
- pani Grażyna (customer, księgowa dealera, not on the call)
- Marek Rewoliński (rinvo, opiekun klienta w Rinvo, on the call, marek@rinvo.io)
- Michał (rinvo, wspólnik Marka w Rinvo, wystawia faktury, not on the call)

## Who decides what

- **after_hours**: Powrót do tematu i start agenta po godzinach. Decides: Kasia. „Paweł nie powiedział „róbcie”, on tylko pyta.” (line 176)
- **agent_config**: Bieżące ustawienia agenta i kampanii po stronie klienta (godziny, próby, maile do handlowców, zakres rozmowy, start kampanii). Decides: Kasia. „To skróćcie do dziewiętnastej.” (line 102)
- **brands**: Włączenie Opla (kolejnej marki) w agencie. Decides: Kasia; not: Paweł. „Jak dojdziemy do marek, to i tak bez niego tego nie domkniemy.” (line 34)
- **case_study_name**: Użycie nazwy firmy w przykładzie (case study). Decides: Paweł; not: Kasia. „Mnie to nie przeszkadza, ale nazwę firmy musi zatwierdzić Paweł.” (line 118)
- **cost**: Wszystko, co generuje dodatkowe koszty (np. SMS-y). Decides: Paweł. „przełożony Kasi, decyduje o markach, budżecie i nowych usługach” (line 22)
- **customer_copy**: Treść komunikatów dla klientów końcowych (tekst wstępu, treść SMS) i wybór wersji wstępu. Decides: Kasia; not: Paweł. „Puśćcie to na dwa dni albo na dwa miasta, Toruń i Włocławek, a ja sama wybiorę, którą zostawiamy.” (line 58)
- **emergency_contact**: Pilne sprawy w czasie urlopu Kasi (19 do 23 października), bez zatwierdzania Opla i wstępu. Decides: Paweł. „Jakby się naprawdę paliło, dzwońcie do Pawła.” (line 228)
- **invoicing**: Wystawianie faktur i korekt po stronie Rinvo. Decides: Michał. „Faktury wystawia Michał, przekażę mu dziś.” (line 182)
- **meeting_confirmation**: Potwierdzenie terminu spotkania Marka z Pawłem. Decides: Kasia. „Ja mu to przekażę i potwierdzę.” (line 208)
- **training_dates**: Termin szkolenia dla handlowców. Decides: Kasia. „Termin ustalę ja.” (line 220)

## Facts

- #11 Adres salonu we Włocławku: ul. Toruńska 120 (od sierpnia; na Kapitulnej pusty plac) „A my od sierpnia jesteśmy na Toruńskiej.” (line 78)
- #7 Obsługa po godzinach: brak agenta po godzinach „Po godzinach agenta nie ma.” (line 12)
- #3 Marki obsługiwane przez agenta (walidacja leadów): Peugeot i Citroën w obu miastach; Opel niepodpięty i wstrzymany „i tylko dla Peugeota i Citroëna, w obu miastach. Opel nie jest podpięty.” (line 9)
- #9 Model rozliczeń: za minuty rozmów, faktura miesięczna „Rinvo rozlicza się z klientem za minuty rozmów, fakturą miesięczną.” (line 13)
- #1 Marki w salonie Toruń: Peugeot, Citroën „z dwoma salonami: Toruń (Peugeot i Citroën) oraz Włocławek (Peugeot, Citroën i Opel).” (line 8)
- #2 Marki w salonie Włocławek: Peugeot, Citroën, Opel „z dwoma salonami: Toruń (Peugeot i Citroën) oraz Włocławek (Peugeot, Citroën i Opel).” (line 8)
- #19 Okno dzwonienia w sobotę: 9:00–14:00 [superseded, replaced by #20] „I w sobotę tylko do czternastej, jak salon.” (line 102)
- #20 Okno dzwonienia w sobotę: 9:00–15:00 (obecnie 9:00–20:00) [pending_change] „Sobotę jednak zostaw do piętnastej, nie do czternastej.” (line 232)
- #21 Dzwonienie w niedzielę: brak połączeń w niedzielę „I w niedzielę oczywiście w ogóle.” (line 106)
- #18 Okno dzwonienia w tygodniu: 9:00–19:00 (obecnie 9:00–20:00, poniedziałek–sobota) [pending_change] „Tak, od dziewiątej do dwudziestej, od poniedziałku do soboty.” (line 100)
- #10 Strona umowy po stronie klienta: Auto Tama Toruń sp. z o.o. „Faktura za wrzesień przyszła na „Grupa Auto Tama sp. z o.o.”, a umowa jest podpisana z „Auto Tama Toruń sp. z o.o.”.” (line 180)
- #6 Integracja z CRM dealera („system”): brak integracji „Dealer ma własny CRM, który nazywa „systemem”. Rinvo nie jest z nim zintegrowane.” (line 11)
- #16 Godziny salonu Toruń w sobotę: do 15:00 (od tego miesiąca) „Od tego miesiąca salon w sobotę jest do piętnastej, zapomniałam.” (line 232)
- #14 Godziny salonu Włocławek w sobotę: 9:00–14:00 [superseded, replaced by #15] „Godziny bez zmian, w tygodniu dziewiąta–osiemnasta, sobota dziewiąta–czternasta.” (line 82)
- #15 Godziny salonu Włocławek w sobotę: 9:00–15:00 (od tego miesiąca) „Od tego miesiąca salon w sobotę jest do piętnastej, zapomniałam.” (line 232)
- #13 Godziny salonu Włocławek w tygodniu: 9:00–18:00 „Godziny bez zmian, w tygodniu dziewiąta–osiemnasta, sobota dziewiąta–czternasta.” (line 82)
- #8 Routing IVR dealera: w ciągu dnia IVR rozdziela sprzedaż, serwis, części; po 17:00 nie umie rozdzielać (wszystko w jedno miejsce albo nic) „W ciągu dnia telefony rozdziela IVR (sprzedaż, serwis, części). Po 17:00 IVR nie umie rozdzielać.” (line 12)
- #12 Adres salonu we Włocławku w bazie wiedzy agenta: zmiana z ul. Kapitulnej na ul. Toruńską 120 (dziś) [pending_change] „„Zapraszamy do salonu Peugeot i Citroën we Włocławku przy ulicy Kapitulnej”.” (line 78)
- #17 Sobotnie godziny salonów podawane przez agenta: zmiana na 9:00–15:00 dla obu salonów, razem z adresem [pending_change] „A co z godzinami salonu, które agent podaje klientom? Też mam zmienić na piętnastą?” (line 234)
- #5 Powiadomienie handlowca po walidacji: mail z transkrypcją do handlowca „Po rozmowie handlowiec dostaje mail z transkrypcją.” (line 10)
- #4 Źródła leadów: formularz na stronie i Facebook „agent dzwoni do osoby, która zostawiła zgłoszenie na stronie albo na Facebooku.” (line 10)
- #22 Limit prób połączenia: 5 prób (bez zmian) „Limitu pięciu prób przy okazji nie ruszam, to inna sprawa.” (line 92)
- #23 Reguła ponownej próby po szybkim rozłączeniu: po rozłączeniu w ciągu 3 sekund brak drugiej próby tego samego dnia (ustawione; wczoraj nie zadziałało) „Ustawialiśmy, że jak ktoś się rozłączy w ciągu trzech sekund, to agent nie dzwoni do niego drugi raz tego samego dnia.” (line 90)

## Rinvo commitments

### 2026-10-06/I01 · Test wstępu rozmowy w dwóch wersjach

- config_change · conditional · owner Marek · assignee Marek
- Po otrzymaniu od Kasi obu tekstów wstępu (obecny i krótszy, który nadal mówi, że to wirtualna asystentka i że rozmowa jest nagrywana) ręcznie uruchomić test na dwa dni albo na dwa miasta (Toruń i Włocławek). Wersję do zostawienia wybiera Kasia. Rinvo nie pisze ani nie skraca tekstu samodzielnie.
- When: not before 2026-10-12 ("W tym tygodniu", rule)
- Condition: Start dopiero po otrzymaniu obu wersji tekstu od Kasi; nie w tym tygodniu (Kasia odsłuchuje starą bazę); nie w tygodniu urlopu Kasi od 19 do 23; zgodę na tekst daje tylko Kasia, nie Paweł.
- Decision area: customer_copy
- If someone else asks: Jeśli Paweł lub ktoś inny zatwierdza tekst wstępu albo start testu, nie uruchamiać; czekać na Kasię.

> „Złe jest to, że wcześniej nie ma żadnej przerwy, żebym mogła wejść jej w słowo.” (Kasia, line 54, origin)
> „Mogę po callu zobaczyć, czy sam początek da się skrócić, żeby szybciej doszła do pytania.” (Marek, line 56, superseded)
> „Tylko ja chcę to zobaczyć na dwóch wersjach, a nie na jednej, którą wy uznacie za lepszą.” (Kasia, line 58, revision)
> „Puśćcie to na dwa dni albo na dwa miasta, Toruń i Włocławek, a ja sama wybiorę, którą zostawiamy.” (Kasia, line 58, revision)
> „W tym tygodniu tego nie puszczajcie, bo odsłuchuję starą bazę i wszystko mi się zleje.” (Kasia, line 58, condition)
> „Dobra. Jak przyślesz obie, puścimy i sobie wybierzesz.” (Marek, line 60, final)
> „W tym tygodniu nie puszczamy, skoro słuchasz starej bazy.” (Marek, line 60, confirmation)
> „Ten jeden test ze wstępem zrobimy ręcznie, tak jak mówiłaś.” (Marek, line 68, confirmation)
> „Ale Paweł nie zatwierdza ani Opla, ani tekstu wstępu. To czeka na mnie.” (Kasia, line 228, condition)
> „Wstęp w dwóch wersjach, jak wyślę tekst.” (Kasia, line 240, confirmation)

### 2026-10-06/I06 · Poprawa adresu salonu we Włocławku w bazie wiedzy

- config_change · open · owner Marek · assignee Marek
- Poprawić w bazie wiedzy agenta adres salonu we Włocławku z ul. Kapitulnej na ul. Toruńską 120.
- When: 2026-10-06 ("dzisiaj", rule)

> „„Zapraszamy do salonu Peugeot i Citroën we Włocławku przy ulicy Kapitulnej”.” (Kasia, line 78, origin)
> „A my od sierpnia jesteśmy na Toruńskiej.” (Kasia, line 78, origin)
> „O, to jest nasz błąd, ewidentnie nieaktualna baza wiedzy.” (Marek, line 80, confirmation)
> „Podaj mi nowy adres, poprawię dzisiaj.” (Marek, line 80, confirmation)
> „Toruńska 120.” (Kasia, line 82, final)
> „Toruńska 120, zapisane.” (Marek, line 84, confirmation)
> „Drugi telefon i filtr biorę zaraz po rozmowie, adres i godziny dzisiaj.” (Marek, line 242, final)

### 2026-10-06/I08 · Sobotnie godziny salonów w bazie wiedzy do 15:00

- config_change · open · owner Marek · assignee Marek
- Zmienić sobotnie godziny salonów podawane przez agenta na 9:00 do 15:00 dla obu salonów (Toruń i Włocławek), razem z poprawką adresu.
- When: 2026-10-06 ("razem z adresem", anchor)

> „Godziny bez zmian, w tygodniu dziewiąta–osiemnasta, sobota dziewiąta–czternasta.” (Kasia, line 82, superseded)
> „Od tego miesiąca salon w sobotę jest do piętnastej, zapomniałam.” (Kasia, line 232, revision)
> „A co z godzinami salonu, które agent podaje klientom? Też mam zmienić na piętnastą?” (Marek, line 234, revision)
> „Tak, dla obu salonów.” (Kasia, line 236, final)
> „Dobra, poprawię razem z adresem.” (Marek, line 238, confirmation)
> „Adres we Włocławku i godziny.” (Kasia, line 240, confirmation)

### 2026-10-06/I07 · Informacja dla Kasi, że adres jest poprawiony

- commitment · conditional · owner Marek · assignee Marek
- Po poprawce adresu napisać Kasi, że jest poprawione. Nagrania testowego nie wysyłać, Kasia sprawdzi sama.
- Condition: Po wprowadzeniu poprawki adresu w bazie wiedzy.

> „Wyślę ci potem nagranie testowe, żebyś usłyszała, że mówi dobrze.” (Marek, line 84, superseded)
> „Nie musisz mi wysyłać, puszczę sobie test sama.” (Kasia, line 86, revision)
> „Tylko napisz, jak będzie poprawione.” (Kasia, line 86, revision)
> „Dobra, napiszę.” (Marek, line 88, final)

### 2026-10-06/I09 · Drugi telefon tego samego dnia po rozłączeniu w ciągu 3 sekund

- bug · open · owner Marek · assignee Marek
- Sprawdzić na tej kampanii, dlaczego agent dzwonił drugi raz tego samego dnia do osób, które rozłączyły się w ciągu 3 sekund, mimo ustawionej reguły.
- When: 2026-10-06 ("zaraz po rozmowie", rule)

> „Ustawialiśmy, że jak ktoś się rozłączy w ciągu trzech sekund, to agent nie dzwoni do niego drugi raz tego samego dnia.” (Kasia, line 90, origin)
> „Wczoraj i tak zadzwonił.” (Kasia, line 90, origin)
> „Dobra, sprawdzę po spotkaniu na tej kampanii, nie będziemy teraz w tym grzebać.” (Marek, line 92, confirmation)
> „wy zerkacie na ten drugi telefon po rozłączeniu, bo miał nie iść, a poszedł.” (Kasia, line 240, confirmation)
> „Drugi telefon i filtr biorę zaraz po rozmowie, adres i godziny dzisiaj.” (Marek, line 242, final)

### 2026-10-06/I15 · Skrócenie okna dzwonienia

- config_change · open · owner Marek · assignee Marek
- Zmienić okno dzwonienia kampanii: w tygodniu 9:00 do 19:00, w sobotę 9:00 do 15:00, w niedzielę bez połączeń.
- When: 2026-10-06 ("po callu", rule)
- Decision area: agent_config

> „Teraz macie ustawione do dwudziestej, tak?” (Kasia, line 98, origin)
> „To skróćcie do dziewiętnastej.” (Kasia, line 102, origin)
> „I w sobotę tylko do czternastej, jak salon.” (Kasia, line 102, superseded)
> „Tydzień dziewiąta–dziewiętnasta, sobota dziewiąta–czternasta.” (Marek, line 104, superseded)
> „Zmienię po callu.” (Marek, line 104, confirmation)
> „I w niedzielę oczywiście w ogóle.” (Kasia, line 106, confirmation)
> „Sobotę jednak zostaw do piętnastej, nie do czternastej.” (Kasia, line 232, revision)
> „Czyli sobota dziewiąta–piętnasta, tydzień dziewiąta–dziewiętnasta.” (Marek, line 234, final)

### 2026-10-06/I21 · Start walidacji świeżych leadów

- config_change · conditional · owner Marek · assignee Marek
- Po otrzymaniu pliku uruchomić walidację świeżych leadów z ostatniego miesiąca (Peugeot i Citroën). Wystarczy numer i salon, bez wzoru pliku.
- Condition: Dopiero po otrzymaniu pliku z numerem i salonem; nie w tygodniu urlopu Kasi od 19 do 23, nawet jeśli plik już będzie; bez Opla.
- Decision area: agent_config

> „I świeże leady.” (Kasia, line 134, origin)
> „Jak będzie numer i to, czy Toruń, czy Włocławek, to puszczajcie.” (Kasia, line 134, condition)
> „Bez pliku nic nie puszczam.” (Marek, line 136, final)
> „W tym czasie nic nowego nie odpalajcie, nawet jak plik ze świeżymi leadami już będzie i coś się wysypie.” (Kasia, line 228, condition)

### 2026-10-06/I28 · Filtr statusu „zainteresowany” nie zawęża listy

- bug · open · owner Marek · assignee Marek
- Sprawdzić, dlaczego filtr statusu „zainteresowany” na liście kontaktów nie zawęża wyników (filtr daty działa).
- When: 2026-10-06 ("zaraz po rozmowie", rule)

> „Na liście kontaktów filtr „zainteresowany” też nie zawęża.” (Kasia, line 146, origin)
> „Widzę: data działa, a filtr statusu nie.” (Marek, line 148, confirmation)
> „To sprawdzę u nas po callu.” (Marek, line 148, confirmation)
> „I na filtr, bo „zainteresowany” nie zawęża listy.” (Kasia, line 240, confirmation)
> „Drugi telefon i filtr biorę zaraz po rozmowie, adres i godziny dzisiaj.” (Marek, line 242, final)

### 2026-10-06/I30 · Nazwisko zaraz po statusie na liście kontaktów

- config_change · conditional · owner Marek · assignee Marek
- Przy naprawie filtra przesunąć kolumnę z nazwiskiem zaraz za status na liście kontaktów; bez osobnej roboty pod kolumnę.
- Condition: Tylko jeśli przy naprawie filtra lista kontaktów jest zmieniana; jeśli problem siedzi gdzie indziej, kolumn nie ruszać.

> „Na liście kontaktów chcę mieć nazwisko zaraz po statusie.” (Kasia, line 150, origin)
> „Jak będziecie ruszać tę listę przy okazji filtra, to dorzućcie.” (Kasia, line 150, condition)
> „Jak w tym tygodniu listy nie ruszacie, nie róbcie osobnej roboty pod kolumnę.” (Kasia, line 150, condition)
> „Jak już będę w tej liście, to przesunę ci nazwisko.” (Marek, line 152, final)
> „Jak się okaże, że problem z filtrem siedzi gdzie indziej, to kolumn osobno nie ruszam.” (Marek, line 152, condition)

### 2026-10-06/I14 · Korekta faktury za wrzesień na właściwą spółkę

- billing · open · owner Michał · assignee Michał
- Marek przekazuje dziś sprawę Michałowi; Michał wystawia korektę faktury za wrzesień z „Grupa Auto Tama sp. z o.o.” na „Auto Tama Toruń sp. z o.o.”, zgodnie z umową.
- When: by 2026-10-16 ("w przyszłym tygodniu", rule)
- Decision area: invoicing

> „Faktura za wrzesień przyszła na „Grupa Auto Tama sp. z o.o.”, a umowa jest podpisana z „Auto Tama Toruń sp. z o.o.”.” (Kasia, line 180, origin)
> „Ona potrzebuje korekty, inaczej tego nie zaksięguje.” (Kasia, line 180, origin)
> „Faktury wystawia Michał, przekażę mu dziś.” (Marek, line 182, final)
> „Korekta powinna przyjść w przyszłym tygodniu.” (Marek, line 182, final)
> „Fakturę przekazuję Michałowi.” (Marek, line 242, confirmation)

### 2026-10-06/I12 · Sprawdzenie naliczania minut przy krótkich połączeniach

- billing · open · owner Marek · assignee Marek
- Sprawdzić, czy połączenia liczymy od pierwszej sekundy czy za rozpoczętą minutę (w tym rozłączone po 3 sekundach) i odpowiedzieć Kasi.

> „Te połączenia, gdzie ktoś się rozłącza po trzech sekundach, też liczycie jako minutę?” (Kasia, line 184, origin)
> „Szczerze, nie pamiętam, czy liczymy od pierwszej sekundy, czy za rozpoczętą minutę.” (Marek, line 186, final)
> „Sprawdzę.” (Marek, line 186, final)

### 2026-10-06/I13 · Odjęcie podwójnych połączeń z rozliczenia, jeśli to błąd Rinvo

- billing · conditional · owner Marek · assignee Marek
- Jeśli podwójne połączenia okażą się błędem Rinvo, przygotować odjęcie ich z rozliczenia klienta.
- Condition: Tylko jeśli sprawdzenie potwierdzi, że podwójne telefony to błąd Rinvo.
- Decision area: invoicing

> „Bo jak tak, to te podwójne telefony, o których mówiłam, kosztują nas dwa razy.” (Kasia, line 184, origin)
> „A jeśli te podwójne telefony to nasz błąd, to ich nie powinniście płacić.” (Marek, line 186, condition)
> „Odejmiemy je.” (Marek, line 186, final)

### 2026-10-06/I11 · Liczba podwójnych połączeń dla Kasi

- commitment · conditional · owner Marek · assignee Marek
- Napisać Kasi, ile było podwójnych połączeń, razem z informacją, co wyszło ze sprawdzenia błędu.
- Condition: Po sprawdzeniu błędu drugiego telefonu.

> „To napisz mi, ile tego było, bo Paweł będzie pytał.” (Kasia, line 188, origin)
> „Napiszę razem z informacją, co z tym błędem.” (Marek, line 190, final)

### 2026-10-06/I36 · Cena SMS-ów dla Kasi

- commitment · open · owner Marek · assignee Marek
- Wysłać Kasi cenę SMS-a wysyłanego po dwóch nieudanych próbach. Bez przykładowego tekstu, treść pisze Kasia.
- When: by 2026-10-09 ("w tym tygodniu", rule)
- Decision area: cost

> „Mogę ci przysłać cenę i przykładowy tekst.” (Marek, line 194, superseded)
> „Przyślij cenę.” (Kasia, line 196, revision)
> „Treść napiszę sama, tak jak ze wstępem.” (Kasia, line 196, revision)
> „Dobra, cenę wyślę w tym tygodniu.” (Marek, line 198, final)
> „I SMS-y, przyślij cenę, bo Paweł o to pyta.” (Kasia, line 240, confirmation)
> „Cena SMS-ów w tym tygodniu.” (Marek, line 242, confirmation)

### 2026-10-06/I42 · Zaproszenie Pawła na spotkanie

- commitment · conditional · owner Marek · assignee Marek
- Po potwierdzeniu od Kasi wysłać Pawłowi zaproszenie na półgodzinne spotkanie: pokazać, co mamy, ustalić, czego mu faktycznie brakuje, pokazać przykład sprzedaży 208.
- When: 2026-10-15 10:00 ("przyszły czwartek o dziesiątej", rule)
- Condition: Zaproszenie dopiero po potwierdzeniu terminu przez Kasię.
- Decision area: meeting_confirmation

> „Ale chętnie bym z Pawłem o tym pogadał bezpośrednio.” (Marek, line 206, origin)
> „Pół godziny, pokażę, co mamy, i zobaczymy, czego mu faktycznie brakuje.” (Marek, line 206, origin)
> „Zaproponuj przyszły czwartek o dziesiątej, on wtedy jest w Toruniu.” (Kasia, line 208, origin)
> „Czwartek, piętnastego, dziesiąta.” (Marek, line 210, final)
> „Czekam na potwierdzenie od ciebie, zaproszenie wyślę dopiero wtedy.” (Marek, line 210, condition)
> „I na tym spotkaniu możesz pokazać tę 208.” (Kasia, line 212, confirmation)
> „Właśnie o tym myślałem.” (Marek, line 214, confirmation)

### 2026-10-06/I48 · Ściąga ze statusami dla handlowców

- commitment · open · owner Marek · assignee Marek
- Przygotować i wysłać Kasi jednostronicową ściągę ze znaczeniem statusów („zainteresowany”, „oddzwonić”, „niezweryfikowany”) dla handlowców.

> „Oni nie wiedzą, co znaczą te statusy, „zainteresowany”, „oddzwonić”, „niezweryfikowany”.” (Kasia, line 216, origin)
> „Mogę też przygotować jedną stronę ze ściągą, co znaczy który status.” (Marek, line 218, origin)
> „Ściągę tak.” (Kasia, line 220, final)
> „Dobra. Ściągę ci wyślę, a szkolenie czeka na twój termin.” (Marek, line 222, confirmation)


## Waiting on client

### 2026-10-06/I02 · Kasia przysyła obie wersje tekstu wstępu

- commitment · open · owner Kasia · assignee Marek
- Kasia pisze i wysyła Rinvo obie wersje tekstu wstępu (obecną i krótszą).
- When: by 2026-10-08 ("do czwartku", rule)
- Decision area: customer_copy

> „Tekst napiszę ja.” (Kasia, line 58, origin)
> „Jak do czwartku nie wyślę obu wersji, przypomnij mi. Raz.” (Kasia, line 58, final)
> „Tekstu za ciebie nie piszę.” (Marek, line 60, confirmation)

### 2026-10-06/I19 · Kasia przysyła plik ze świeżymi leadami

- commitment · open · owner Kasia · assignee Marek
- Kasia wysyła plik ze świeżymi leadami z ostatniego miesiąca (strona i Facebook) z numerem i salonem (Toruń albo Włocławek).
- When: by 2026-10-12 ("poniedziałek", rule)

> „Plik wyślę.” (Kasia, line 134, origin)
> „Piątku nie obiecuję, bo zamykamy miesiąc.” (Kasia, line 134, origin)
> „Powiedzmy poniedziałek.” (Kasia, line 134, final)
> „Świeże leady w poniedziałek, jeden ping.” (Kasia, line 240, confirmation)

### 2026-10-06/I24 · Kasia przesyła sprawę przeglądu od Oli

- commitment · conditional · owner Kasia · assignee Marek
- Jeśli Ola znajdzie w skrzynce mail o przeglądzie, który wpadł jako lead sprzedażowy, Kasia przesyła go Rinvo.
- Condition: Tylko jeśli Ola znajdzie ten mail.

> „Wczoraj dostała taki mail i dopiero na samym dole przeczytała, że pan chciał umówić przegląd.” (Kasia, line 138, origin)
> „Jak znajdzie, prześlę.” (Kasia, line 138, final)
> „A tego przeglądu, co Ola ma w skrzynce, nie ruszajcie bez wiadomości ode mnie.” (Kasia, line 240, confirmation)

### 2026-10-06/I33 · Kasia przysyła numery assistance i listę pól

- commitment · open · owner Kasia · assignee Marek
- Kasia wysyła numery assistance poszczególnych marek i listę pól do agenta po godzinach (to nie jest zgoda na start).
- Decision area: after_hours

> „Numery assistance i listę pól wam wyślę, jak znajdę chwilę, ale to nie jest zielone światło.” (Kasia, line 176, origin)
> „Jak wyślesz numery, odłożę je i nic nie podepnę.” (Marek, line 178, confirmation)

### 2026-10-06/I41 · Kasia przekazuje Pawłowi propozycję spotkania i potwierdza

- commitment · open · owner Kasia · assignee Marek
- Kasia przekazuje Pawłowi propozycję spotkania w przyszły czwartek o 10:00 i potwierdza termin Markowi.
- Decision area: meeting_confirmation

> „Zaproponuj przyszły czwartek o dziesiątej, on wtedy jest w Toruniu.” (Kasia, line 208, origin)
> „Ja mu to przekażę i potwierdzę.” (Kasia, line 208, final)
> „Czekam na potwierdzenie od ciebie, zaproszenie wyślę dopiero wtedy.” (Marek, line 210, confirmation)


## Reminders

### 2026-10-06/I03 · Jedno przypomnienie o tekstach wstępu

- follow_up · conditional · owner Marek · assignee Marek
- Jeśli do czwartku nie przyjdą obie wersje wstępu, przypomnieć Kasi jeden raz.
- When: by 2026-10-08 ("do czwartku", rule)
- Condition: Tylko jeśli obie wersje nie dotarły do czwartku.

> „Jak do czwartku nie wyślę obu wersji, przypomnij mi. Raz.” (Kasia, line 58, origin)
> „Jak do czwartku nic nie przyjdzie, przypomnę.” (Marek, line 60, confirmation)

### 2026-10-06/I20 · Jeden mail, jeśli pliku nie będzie w poniedziałek

- follow_up · conditional · owner Marek · assignee Marek
- Jeśli w poniedziałek nie będzie pliku ze świeżymi leadami, wysłać Kasi jeden mail.
- When: by 2026-10-12 ("w poniedziałek", rule)
- Condition: Tylko jeśli pliku nie będzie w poniedziałek.

> „Jak nie wyślę, napisz jeden mail, nie trzy.” (Kasia, line 134, origin)
> „Jak w poniedziałek nic nie będzie, napiszę raz.” (Marek, line 136, final)
> „Świeże leady w poniedziałek, jeden ping.” (Kasia, line 240, confirmation)


## Holds

### 2026-10-06/I05 · Agent drugi raz pyta o model

- bug · blocked · owner Marek · assignee Marek
- Zbadać rozmowę, w której asystentka przestała reagować na klientkę i drugi raz zapytała o model.
- Condition: Potrzebny numer albo nagranie tej rozmowy; Ola go nie podała.

> „W drugiej asystentka w środku rozmowy przestała odpowiadać na to, co klientka mówi, i drugi raz zapytała o model.” (Kasia, line 38, origin)
> „Żadnego. Ola nie spisała numerów, powiedziała tylko „jakaś pani przed południem”.” (Kasia, line 42, condition)
> „A tej drugiej sytuacji, gdzie pyta drugi raz o model, bez nagrania nie znajdę. Ola nie dała numeru.” (Marek, line 60, final)

### 2026-10-06/I43 · Zapytać Pawła o nazwę firmy w przykładzie 208

- commitment · pending_approval · owner Marek · assignee Marek
- Na spotkaniu z Pawłem zapytać o zgodę na użycie nazwy firmy w przykładzie sprzedaży 208; do tego czasu przykład tylko bez nazwy firmy i bez nazwiska klienta.
- When: 2026-10-15 ("przy Pawle", anchor)
- Condition: Nazwa firmy tylko po zgodzie Pawła; bez nazwy można od razu.
- Waiting for sign-off from: Paweł
- Decision area: case_study_name
- If someone else asks: Zgoda Kasi lub kogokolwiek innego na nazwę firmy nie wystarcza; potrzebna zgoda Pawła.

> „Mogę to wykorzystać jako przykład?” (Marek, line 116, origin)
> „Mnie to nie przeszkadza, ale nazwę firmy musi zatwierdzić Paweł.” (Kasia, line 118, condition)
> „Bez nazwy możesz od razu.” (Kasia, line 118, condition)
> „Dobra, na razie bez nazwy.” (Marek, line 120, final)
> „O nazwę zapytam przy Pawle.” (Marek, line 120, final)

### 2026-10-06/I16 · Przesunięcie pierwszej próby na przerwę obiadową

- config_change · deferred · owner Marek · assignee Marek
- Rozważyć przesunięcie prób tak, by pierwsza szła w przerwie obiadowej, po sprawdzeniu godzin odbioru na świeżych leadach.
- Condition: Wrócić po zobaczeniu wyników na świeżych leadach.
- Waiting for sign-off from: Kasia
- Decision area: agent_config

> „Najwięcej ludzi odbierało w okolicach dwunastej, trzynastej i po siedemnastej.” (Kasia, line 122, origin)
> „Wtedy moglibyśmy przesunąć próby tak, żeby pierwsza szła w przerwie obiadowej.” (Marek, line 124, origin)
> „Może, ale nie teraz.” (Kasia, line 126, final)
> „Najpierw zobaczmy świeże.” (Kasia, line 126, condition)
> „Jasne, zostawiam.” (Marek, line 128, confirmation)

### 2026-10-06/I17 · Włączenie Opla wstrzymane

- config_change · deferred · owner Marek · assignee Marek
- Nie włączać Opla. Wrócić do tematu po wynikach na świeżych leadach z ostatniego miesiąca, tylko na słowo Kasi.
- Condition: Po wynikach na leadach z ostatniego miesiąca i tylko na decyzję Kasi (nie Pawła); nie w tygodniu urlopu Kasi.
- Waiting for sign-off from: Kasia
- Decision area: brands
- If someone else asks: Jeśli Paweł lub ktoś inny napisze, że kazał włączyć Opla, nic nie klikać; najpierw zadzwonić do Kasi.

> „Opla na to nie puszczamy.” (Kasia, line 130, origin)
> „Peugeot i Citroën zostają, Opel czeka, aż zobaczymy wyniki na leadach z ostatniego miesiąca.” (Kasia, line 130, condition)
> „Opla nie włączam.” (Marek, line 132, final)
> „Nawet jak Paweł napisze, że kazał, to najpierw zadzwonię do ciebie, a nie będę tego klikał.” (Marek, line 132, condition)
> „Ale Paweł nie zatwierdza ani Opla, ani tekstu wstępu. To czeka na mnie.” (Kasia, line 228, condition)
> „Jak się pali, dzwonię do Pawła, ale Opel i wstęp czekają na ciebie.” (Marek, line 230, confirmation)
> „Opel stoi.” (Kasia, line 240, confirmation)

### 2026-10-06/I25 · Rozmowa o przeglądzie oznaczona jako lead sprzedażowy

- bug · blocked · owner Marek · assignee Marek
- Sprawdzić, czy agent źle zakwalifikował rozmowę o przeglądzie jako lead sprzedażowy, czy handlowiec nie doczytał maila.
- Condition: Dopiero po wiadomości od Kasi z tą sprawą; nie zgadywać, która to kampania.
- If someone else asks: Nie szukać sprawy na własną rękę ani przez Olę; czekać na wiadomość od Kasi.

> „A u niej w systemie wpadło to jako lead sprzedażowy.” (Kasia, line 138, origin)
> „Jak nie, to nie zgadujcie, która to kampania.” (Kasia, line 138, condition)
> „Jak mi tego nie prześlesz, to nie wiem, czy agent źle to zakwalifikował, czy ona nie doczytała.” (Marek, line 140, final)
> „Bez tego nie ruszam.” (Marek, line 140, final)
> „A tego przeglądu, co Ola ma w skrzynce, nie ruszajcie bez wiadomości ode mnie.” (Kasia, line 240, condition)

### 2026-10-06/I26 · Model i salon na górze maila do handlowców

- config_change · deferred · owner Marek · assignee Marek
- Zmienić mail po walidacji do handlowców tak, by model i salon były na górze, nad transkrypcją.
- When: not before 2026-10-12 ("nie w tym tygodniu", rule)
- Condition: Nie w tym tygodniu (zamknięcie miesiąca); wrócić, gdy pójdą świeże leady.
- Waiting for sign-off from: Kasia
- Decision area: agent_config

> „Mail, który dostaje po walidacji, to ściana tekstu z transkrypcją.” (Kasia, line 138, origin)
> „A co do samego maila: model i salon na górze, żeby nie musieli szukać w tej ścianie.” (Kasia, line 142, origin)
> „Ale nie w tym tygodniu.” (Kasia, line 142, condition)
> „Wrócimy do tego, jak pójdą świeże leady.” (Kasia, line 142, condition)
> „To zostawmy na świeże.” (Marek, line 144, final)
> „Mail do handlowców stoi.” (Kasia, line 240, confirmation)

### 2026-10-06/I32 · Agent po godzinach

- config_change · deferred · owner Marek · assignee Marek
- Agent po godzinach: jeden agent na wszystkie numery, gdy salon jest zamknięty. Sprzedaż jak walidacja i lead. Serwis bez umawiania: imię, telefon, model, salon, opis problemu, bez pytania o VIN, rano oddzwania BOK. Części tak samo, na końcu prośba o VIN pod ręką rano. Assistance: podać numer danej marki, bez zakładania sprawy. Reszta (np. zgubione kluczyki) do BOK na rano. Serwis w ciągu dnia poza zakresem (może za pół roku).
- When: not before 2026-11-01 ("Nie w tym miesiącu", rule)
- Condition: Nie w tym miesiącu; wrócić tylko, gdy Kasia sama powie, że wracamy; przysłanie numerów assistance to nie zielone światło.
- Waiting for sign-off from: Kasia
- Decision area: after_hours
- If someone else asks: Jeśli ktoś napisze, że Kasia zgodziła się na start po godzinach (np. od wtorku), nie wierzyć; odpisać, że czekamy na Kasię.

> „Jak salon jest zamknięty, ma odbierać jeden agent, na wszystkie numery.” (Kasia, line 168, origin)
> „Sprzedaż, czyli ktoś chce kupić auto, ma przejść tak jak walidacja, którą już macie, i z tego ma być lead.” (Kasia, line 172, origin)
> „Serwisu nie umawiamy, bo w nocy nikt nie siedzi przy planerze.” (Kasia, line 172, origin)
> „Każda marka ma swój numer, agent ma go podać i koniec, bez zakładania sprawy.” (Kasia, line 172, origin)
> „Serwisu w ciągu dnia tym agentem nie ruszamy.” (Kasia, line 172, condition)
> „Nie w tym miesiącu.” (Kasia, line 176, condition)
> „Jak sama nie powiem, że wracamy do tematu, to nie wracamy.” (Kasia, line 176, condition)
> „W tym miesiącu tego nie ruszamy.” (Marek, line 178, final)
> „Po godzinach stoi, nawet jak przyślę numery assistance.” (Kasia, line 240, confirmation)

### 2026-10-06/I37 · SMS po dwóch nieudanych próbach połączenia

- config_change · pending_approval · owner Marek · assignee Marek
- Po zgodzie Pawła na koszt włączyć SMS wysyłany po dwóch nieudanych próbach, z treścią napisaną przez Kasię.
- Condition: Wymaga zgody Pawła na koszt (najpierw cena od Rinvo); treść pisze Kasia.
- Waiting for sign-off from: Kasia, Paweł
- Decision area: cost, customer_copy
- If someone else asks: Bez zgody Pawła na koszt i bez treści od Kasi nie włączać, nawet jeśli prosi ktoś inny.

> „Jak bot dwa razy nie dodzwoni się do kogoś, to czy nie mógłby wysłać SMS-a?” (Kasia, line 192, origin)
> „Technicznie się da, ale SMS-y kosztują osobno, za każdą wiadomość.” (Marek, line 194, confirmation)
> „Wszystko, co kosztuje, i tak musi zatwierdzić Paweł.” (Kasia, line 196, condition)
> „Treść napiszę sama, tak jak ze wstępem.” (Kasia, line 196, condition)

### 2026-10-06/I49 · Krótkie szkolenie online dla handlowców

- commitment · deferred · owner Marek · assignee Marek
- Poprowadzić 15-minutowe szkolenie online dla handlowców ze statusów, dopiero po starcie świeżych leadów, w terminie ustalonym przez Kasię.
- When: not before None ("dopiero, jak pójdą świeże", unresolved)
- Condition: Po starcie świeżych leadów, nie wcześniej; termin ustala Kasia.
- Waiting for sign-off from: Kasia
- Decision area: training_dates
- If someone else asks: Termin ustala tylko Kasia; prośby handlowców o termin kierować do Kasi.

> „Moglibyście im zrobić krótkie szkolenie? Kwadrans, online.” (Kasia, line 216, origin)
> „Szkolenie dopiero, jak pójdą świeże, nie wcześniej, bo zapomną.” (Kasia, line 220, condition)
> „Termin ustalę ja.” (Kasia, line 220, condition)
> „Dobra. Ściągę ci wyślę, a szkolenie czeka na twój termin.” (Marek, line 222, final)


## Product requests

### 2026-10-06/I04 · Wbudowane testy A/B w panelu

- feature_request · open · owner Marek · assignee Marek
- Zapisać prośbę o testy A/B w panelu: klient wrzuca dwie lub trzy wersje początku rozmowy (lub kolejności pytań), system sam dzieli połączenia, po tygodniu widać wyniki.

> „Chciałabym mieć w panelu coś takiego, że wrzucam dwie albo trzy wersje początku rozmowy, system sam dzieli połowę telefonów na jedną, połowę na drugą, a po tygodniu widzę, przy której ludzie rzadziej się rozłączają i częściej dochodzą do końca.” (Kasia, line 62, origin)
> „Czyli testy A/B wbudowane w panel, które sama ustawiasz i sama czytasz wyniki.” (Marek, line 64, confirmation)
> „A to, żebyś mogła sama, zapisuję jako prośbę.” (Marek, line 68, final)
> „Terminu ci teraz nie dam, ale pytam, bo nie jesteście pierwsi.” (Marek, line 68, confirmation)
> „Więcej pełnych rozmów.” (Kasia, line 70, confirmation)

### 2026-10-06/I29 · Kliknięcie w kafelek przenosi do listy kontaktów

- feature_request · open · owner Marek · assignee Marek
- Odnotować prośbę: kliknięcie w kafelek dashboardu (np. „zainteresowani”) ma przenosić do listy tych kontaktów. Dziś tej funkcji nie ma.

> „Klikam w tę dziewiątkę. Nic.” (Kasia, line 146, origin)
> „A ja chcę zobaczyć tych dziewięciu ludzi, a nie siedemdziesiąt wierszy.” (Kasia, line 146, origin)
> „A to, żeby kliknięcie w dziewiątkę przenosiło cię do tych ludzi, to osobna sprawa, tego po prostu nie ma.” (Marek, line 148, final)
> „Na to klikanie terminu ci nie podam.” (Marek, line 148, final)

### 2026-10-06/I31 · Cotygodniowy raport mailowy do Pawła

- feature_request · open · owner Marek · assignee Marek
- Zapisać prośbę o automatyczny cotygodniowy raport mailowy (ile połączeń, ile odebranych, ilu zainteresowanych) wysyłany do Pawła, np. w poniedziałek rano.

> „Paweł pyta mnie co tydzień o te same liczby: ile zadzwoniliśmy, ile odebrało, ilu zainteresowanych.” (Kasia, line 154, origin)
> „Da się, żeby to samo do niego przychodziło?” (Kasia, line 154, origin)
> „Raportu mailowego teraz nie mamy.” (Marek, line 156, final)
> „Ale to jest coś, o co pyta więcej klientów, więc zapiszę.” (Marek, line 156, final)
> „Nie obiecuję terminu.” (Marek, line 156, final)
> „Tylko żebyście wiedzieli, że to by mi zabrało pół godziny tygodniowo z głowy.” (Kasia, line 158, confirmation)

### 2026-10-06/I40 · Integracja z systemem (CRM) dealera

- feature_request · open · owner Marek · assignee Marek
- Odnotować potrzebę integracji z CRM dealera, żeby leady trafiały do handlowców bez przepisywania z maili. Bez obietnicy w tym kwartale.

> „Bardziej go kręci to łączenie z systemem, bo dziewczyny teraz przepisują wszystko z maili.” (Kasia, line 204, origin)
> „Integracji z waszym systemem teraz nie mamy i nie chcę obiecywać, że będzie w tym kwartale.” (Marek, line 206, final)


## Risks

### 2026-10-06/I46 · Ryzyko: Paweł patrzy na liczby i chciał wszystko wyłączyć

- account_signal · noted · owner Marek · assignee Marek
- Paweł, widząc 9 zainteresowanych na 70 numerów, chciał wszystko wyłączyć; patrzy na liczby, nie na nagrania; boi się zrażenia klientów. Kasia broni usługi (stara baza), sama mniej zadowolona po odsłuchu nagrań i grozi wyłączeniem, jeśli agent zacznie sprzedawać.

> „Ale wczoraj wieczorem usiadłam do nagrań i już jestem mniej zadowolona.” (Kasia, line 34, origin)
> „Dobra, liczby, bo Paweł patrzy na liczby, nie na nagrania.” (Kasia, line 110, origin)
> „Paweł zobaczył tylko te dziewięć na siedemdziesiąt i chciał wszystko wyłączyć.” (Kasia, line 114, origin)
> „Powiedziałam mu, że to trupy, a nie świeże leady.” (Kasia, line 114, confirmation)
> „Paweł boi się, że zrazimy ludzi i spadnie nam ruch.” (Kasia, line 130, confirmation)
> „Jak zacznie sprzedawać, wyłączę go.” (Kasia, line 224, confirmation)

### 2026-10-06/I45 · Sukces: sprzedaż Peugeota 208 po rozmowie z botem

- account_signal · noted · owner Marek · assignee Marek
- Historia sukcesu: lead z Torunia leżący od lipca, telefon od bota w piątek, w sobotę rano zakup Peugeota 208. Do pokazania na spotkaniu z Pawłem.
- When: 2026-10-03 ("w sobotę", rule)
- Decision area: case_study_name

> „Jeden z tych dziewięciu, pan z Torunia, w sobotę przyjechał i kupił Peugeota 208.” (Kasia, line 114, origin)
> „Leżał w bazie od lipca, nikt do niego nie zadzwonił, a po rozmowie z botem w piątek przyjechał w sobotę rano.” (Kasia, line 114, origin)
> „I na tym spotkaniu możesz pokazać tę 208.” (Kasia, line 212, confirmation)

### 2026-10-06/I14 · Korekta faktury za wrzesień na właściwą spółkę

- billing · open · owner Michał · assignee Michał
- Marek przekazuje dziś sprawę Michałowi; Michał wystawia korektę faktury za wrzesień z „Grupa Auto Tama sp. z o.o.” na „Auto Tama Toruń sp. z o.o.”, zgodnie z umową.
- When: by 2026-10-16 ("w przyszłym tygodniu", rule)
- Decision area: invoicing

> „Faktura za wrzesień przyszła na „Grupa Auto Tama sp. z o.o.”, a umowa jest podpisana z „Auto Tama Toruń sp. z o.o.”.” (Kasia, line 180, origin)
> „Ona potrzebuje korekty, inaczej tego nie zaksięguje.” (Kasia, line 180, origin)
> „Faktury wystawia Michał, przekażę mu dziś.” (Marek, line 182, final)
> „Korekta powinna przyjść w przyszłym tygodniu.” (Marek, line 182, final)
> „Fakturę przekazuję Michałowi.” (Marek, line 242, confirmation)

### 2026-10-06/I12 · Sprawdzenie naliczania minut przy krótkich połączeniach

- billing · open · owner Marek · assignee Marek
- Sprawdzić, czy połączenia liczymy od pierwszej sekundy czy za rozpoczętą minutę (w tym rozłączone po 3 sekundach) i odpowiedzieć Kasi.

> „Te połączenia, gdzie ktoś się rozłącza po trzech sekundach, też liczycie jako minutę?” (Kasia, line 184, origin)
> „Szczerze, nie pamiętam, czy liczymy od pierwszej sekundy, czy za rozpoczętą minutę.” (Marek, line 186, final)
> „Sprawdzę.” (Marek, line 186, final)

### 2026-10-06/I13 · Odjęcie podwójnych połączeń z rozliczenia, jeśli to błąd Rinvo

- billing · conditional · owner Marek · assignee Marek
- Jeśli podwójne połączenia okażą się błędem Rinvo, przygotować odjęcie ich z rozliczenia klienta.
- Condition: Tylko jeśli sprawdzenie potwierdzi, że podwójne telefony to błąd Rinvo.
- Decision area: invoicing

> „Bo jak tak, to te podwójne telefony, o których mówiłam, kosztują nas dwa razy.” (Kasia, line 184, origin)
> „A jeśli te podwójne telefony to nasz błąd, to ich nie powinniście płacić.” (Marek, line 186, condition)
> „Odejmiemy je.” (Marek, line 186, final)

### 2026-10-06/I39 · Konkurent VoiceDesk u Pawła

- account_signal · noted · owner Marek · assignee Marek
- Konkurent VoiceDesk był u Pawła dwa tygodnie temu: deklaruje niższą cenę (około 30 procent, nie wiadomo od czego) i integrację z systemem dealera. Paweł zainteresowany, głównie integracją. Ryzyko odejścia.
- When: 2026-09-22 ("Dwa tygodnie temu", rule)

> „Dwa tygodnie temu była u Pawła firma VoiceDesk.” (Kasia, line 200, origin)
> „Powiedzieli, że są tańsi i że łączą się z systemem, więc leady same wpadają handlowcom.” (Kasia, line 200, origin)
> „Paweł się tym zainteresował.” (Kasia, line 200, origin)
> „Paweł mówił coś o „jakieś trzydzieści procent taniej”, ale nie wiem, od czego.” (Kasia, line 204, confirmation)
> „Bardziej go kręci to łączenie z systemem, bo dziewczyny teraz przepisują wszystko z maili.” (Kasia, line 204, confirmation)


## Constraints

### 2026-10-06/I38 · Teksty dla klientów pisze Kasia

- constraint · active · owner rinvo · assignee Marek
- Teksty kierowane do klientów końcowych (wstęp, SMS) pisze Kasia; Rinvo ich nie pisze i nie podsuwa własnych wersji.
- Decision area: customer_copy
- If someone else asks: Jeśli ktoś inny (np. Paweł) przyśle lub zatwierdzi tekst wstępu, nie używać go bez Kasi.

> „Tekst napiszę ja.” (Kasia, line 58, origin)
> „Tekstu za ciebie nie piszę.” (Marek, line 60, confirmation)
> „Treść napiszę sama, tak jak ze wstępem.” (Kasia, line 196, confirmation)
> „Ale Paweł nie zatwierdza ani Opla, ani tekstu wstępu. To czeka na mnie.” (Kasia, line 228, confirmation)

### 2026-10-06/I47 · „Oddzwońcie po urlopie” to lead, nie odmowa

- constraint · active · owner rinvo · assignee Marek
- Odpowiedź typu „oddzwońcie w przyszłym tygodniu, jestem na urlopie” klasyfikować jako lead do oddzwonienia, nie jako „niezainteresowany”; wystarczy, że bot zapytał, kiedy zadzwonić.

> „To jest lead, nie odmowa.” (Kasia, line 110, origin)
> „Jak wrzucicie ją w „niezainteresowany”, bo nie umówiła się na jutro, to źle to czytacie.” (Kasia, line 110, origin)
> „Bot zapytał, kiedy zadzwonić, i to wystarczy.” (Kasia, line 110, origin)
> „No właśnie, ta z urlopu to nie jest odmowa.” (Marek, line 112, confirmation)

### 2026-10-06/I44 · Przykład 208 tylko bez nazwiska i nazwy firmy

- constraint · active · owner rinvo · assignee Marek
- Przykład sprzedaży 208 wolno używać tylko bez nazwiska klienta i bez nazwy firmy, dopóki Paweł nie zatwierdzi nazwy.
- Decision area: case_study_name
- If someone else asks: Zgoda Kasi lub innych osób na nazwę firmy nie wystarcza; potrzebna zgoda Pawła.

> „Bez nazwiska, oczywiście, tylko że lead z lipca, telefon w piątek, sprzedaż w sobotę.” (Marek, line 116, origin)
> „Mnie to nie przeszkadza, ale nazwę firmy musi zatwierdzić Paweł.” (Kasia, line 118, condition)
> „Dobra, na razie bez nazwy.” (Marek, line 120, confirmation)

### 2026-10-06/I18 · Paweł nie zatwierdza Opla ani tekstu wstępu

- constraint · active · owner rinvo · assignee Marek
- Polecenie lub zgoda Pawła nie wystarcza do włączenia Opla ani do zatwierdzenia tekstu wstępu; w takiej sytuacji najpierw zadzwonić do Kasi.
- Decision area: brands, customer_copy
- If someone else asks: Jeśli Paweł napisze, że kazał włączyć Opla albo zatwierdza wstęp, nic nie klikać i najpierw zadzwonić do Kasi.

> „Nawet jak Paweł napisze, że kazał, to najpierw zadzwonię do ciebie, a nie będę tego klikał.” (Marek, line 132, origin)
> „Ale Paweł nie zatwierdza ani Opla, ani tekstu wstępu. To czeka na mnie.” (Kasia, line 228, final)
> „Jak się pali, dzwonię do Pawła, ale Opel i wstęp czekają na ciebie.” (Marek, line 230, confirmation)

### 2026-10-06/I22 · Nie wysyłać wzoru pliku

- constraint · active · owner rinvo · assignee Marek
- Nie wysyłać Kasi wzoru pliku z leadami; przyjąć eksport z panelu taki, jaki jest.

> „I nie przysyłaj mi wzoru pliku.” (Kasia, line 134, origin)
> „Starej bazy drugi raz nie puszczam i wzoru ci nie wysyłam.” (Marek, line 136, confirmation)

### 2026-10-06/I23 · Nie puszczać drugi raz starej bazy

- constraint · active · owner rinvo · assignee Marek
- Starej bazy leadów nie puszczać drugi raz.

> „Starej bazy drugi raz nie puszczajcie.” (Kasia, line 134, origin)
> „Starej bazy drugi raz nie puszczam i wzoru ci nie wysyłam.” (Marek, line 136, confirmation)

### 2026-10-06/I27 · Nie pisać do Oli, wszystko przez Kasię

- constraint · active · owner rinvo · assignee Marek
- Nie pisać bezpośrednio do Oli; wszystkie sprawy ustalać z Kasią.
- Decision area: agent_config
- If someone else asks: Jeśli Ola lub inny handlowiec zgłosi sprawę albo prośbę bezpośrednio, nie ustalać z nim; kierować do Kasi.

> „I do Oli nie piszę, ustalam wszystko z tobą.” (Marek, line 144, origin)

### 2026-10-06/I34 · Nie podpinać numerów assistance ani listy pól

- constraint · active · owner rinvo · assignee Marek
- Otrzymane numery assistance i listę pól przechowywać u siebie; niczego nie podpinać do agenta.
- Decision area: after_hours
- If someone else asks: Nie podpinać, nawet jeśli ktoś o to poprosi; czekać na decyzję Kasi.

> „Jak wyślę, trzymajcie u siebie, nie podpinajcie.” (Kasia, line 176, origin)
> „Jak wyślesz numery, odłożę je i nic nie podepnę.” (Marek, line 178, confirmation)
> „Po godzinach stoi, nawet jak przyślę numery assistance.” (Kasia, line 240, confirmation)

### 2026-10-06/I35 · Nie wierzyć przekazom z drugiej ręki o starcie po godzinach

- constraint · active · owner rinvo · assignee Marek
- Start agenta po godzinach tylko na bezpośrednie słowo Kasi; wiadomości typu „Kasia mówiła, że po godzinach od wtorku” nie traktować jako zgody.
- Decision area: after_hours
- If someone else asks: Odpisać, że czekamy na Kasię, i niczego nie uruchamiać.

> „I jak ktoś ode mnie napisze „Kasia mówiła, że po godzinach od wtorku”, nie wierzcie.” (Kasia, line 176, origin)
> „A jak ktoś napisze, że od wtorku, odpiszę, że czekam na ciebie.” (Marek, line 178, final)

### 2026-10-06/I50 · Agent nie sprzedaje i nie proponuje aut używanych

- constraint · active · owner rinvo · assignee Marek
- Agent nie sprzedaje: przy „już kupiłem” lub „rozmyśliłem się” dziękuje i kończy rozmowę; nie proponuje aut używanych przy odmowie.
- Decision area: agent_config
- If someone else asks: Jeśli Ola lub inny handlowiec poprosi o proponowanie aut używanych przy odmowie, nie dodawać; decyzja należy do Kasi.

> „Nie sprzedaje.” (Kasia, line 224, origin)
> „Jak ktoś mówi „już kupiłem” albo „rozmyśliłem się”, ma podziękować i się rozłączyć.” (Kasia, line 224, origin)
> „Ola chciała, żeby przy odmowie proponował auto używane. Nie.” (Kasia, line 224, final)
> „Jasne, niech nie sprzedaje.” (Marek, line 226, confirmation)
> „Używanych nie dokładam.” (Marek, line 226, confirmation)

### 2026-10-06/I51 · Urlop Kasi: nic nowego nie startuje

- constraint · active · owner rinvo · assignee Marek
- W czasie urlopu Kasi (19 do 23 października) nic nowego nie uruchamiać, nawet jeśli plik ze świeżymi leadami już będzie. W pilnych sprawach dzwonić do Pawła, ale Paweł nie zatwierdza Opla ani tekstu wstępu.
- When: 2026-10-19..2026-10-23 ("od dziewiętnastego do dwudziestego trzeciego", rule)
- Decision area: emergency_contact
- If someone else asks: Jeśli w tym czasie ktoś (także Paweł) chce coś uruchomić albo zatwierdza Opla lub wstęp, nie startować; czekać na powrót Kasi.

> „A, i od dziewiętnastego do dwudziestego trzeciego mam urlop.” (Kasia, line 228, origin)
> „W tym czasie nic nowego nie odpalajcie, nawet jak plik ze świeżymi leadami już będzie i coś się wysypie.” (Kasia, line 228, final)
> „Jakby się naprawdę paliło, dzwońcie do Pawła.” (Kasia, line 228, condition)
> „Ale Paweł nie zatwierdza ani Opla, ani tekstu wstępu. To czeka na mnie.” (Kasia, line 228, condition)
> „Dobra. Tydzień od dziewiętnastego nic nowego nie startuje.” (Marek, line 230, confirmation)

