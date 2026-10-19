# Configuration change specs

For a person to apply by hand. The system has no write access to the agent configuration.

### 2026-10-06/I01 · Test wstępu rozmowy w dwóch wersjach

- config_change · conditional · owner Marek · assignee Marek
- Po otrzymaniu od Kasi obu tekstów wstępu (obecny i krótszy, który nadal mówi, że to wirtualna asystentka i że rozmowa jest nagrywana) ręcznie uruchomić test na dwa dni albo na dwa miasta (Toruń i Włocławek). Wersję do zostawienia wybiera Kasia. Rinvo nie pisze ani nie skraca tekstu samodzielnie.
- When: not before 2026-10-12 ("W tym tygodniu", rule)
- Condition: Start dopiero po otrzymaniu obu wersji tekstu od Kasi; nie w tym tygodniu (Kasia odsłuchuje starą bazę); nie w tygodniu urlopu Kasi od 19 do 23; zgodę na tekst daje tylko Kasia, nie Paweł.
- Decision area: customer_copy
- If someone else asks: Jeśli Paweł lub ktoś inny zatwierdza tekst wstępu albo start testu, nie uruchamiać; czekać na Kasię.
- Status: **HOLD until the condition holds**
- Setting: wstęp rozmowy walidacyjnej
- Current: jedna wersja wstępu: formułka o nagrywaniu i wirtualnej asystentce bez przerwy na wejście w słowo
- New: dwie wersje: obecna i krótsza (nadal z informacją o wirtualnej asystentce i nagrywaniu), podział na dwa dni albo na dwa miasta
- Earliest start: 2026-10-12; blocked: 2026-10-06..2026-10-11 (2026-10-06/I01), 2026-10-19..2026-10-23 (2026-10-06/I51)

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
- Status: **APPLY after review**
- Setting: baza wiedzy: adres salonu Włocławek
- Current: ul. Kapitulna
- New: ul. Toruńska 120

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
- Status: **APPLY after review**
- Setting: baza wiedzy: godziny salonów w sobotę
- Current: sobota dziewiąta–czternasta
- New: sobota 9:00–15:00, oba salony

> „Godziny bez zmian, w tygodniu dziewiąta–osiemnasta, sobota dziewiąta–czternasta.” (Kasia, line 82, superseded)
> „Od tego miesiąca salon w sobotę jest do piętnastej, zapomniałam.” (Kasia, line 232, revision)
> „A co z godzinami salonu, które agent podaje klientom? Też mam zmienić na piętnastą?” (Marek, line 234, revision)
> „Tak, dla obu salonów.” (Kasia, line 236, final)
> „Dobra, poprawię razem z adresem.” (Marek, line 238, confirmation)
> „Adres we Włocławku i godziny.” (Kasia, line 240, confirmation)

### 2026-10-06/I10 · Obniżenie limitu prób z 5 do 3 (odrzucone)

- config_change · rejected · owner Marek · assignee Marek
- Nie zmieniać limitu 5 prób; obniżenie do 3 nie zostało zlecone.
- Decision area: agent_config
- Status: **DO NOT APPLY (rejected)**
- Setting: limit prób połączenia
- Current: 5
- New: 5 (bez zmian)

> „Limitu pięciu prób przy okazji nie ruszam, to inna sprawa.” (Marek, line 92, origin)
> „Zostaw pięć.” (Kasia, line 94, final)
> „Nie kazałam schodzić do trzech.” (Kasia, line 94, final)
> „No, zostaje pięć.” (Marek, line 96, confirmation)

### 2026-10-06/I15 · Skrócenie okna dzwonienia

- config_change · open · owner Marek · assignee Marek
- Zmienić okno dzwonienia kampanii: w tygodniu 9:00 do 19:00, w sobotę 9:00 do 15:00, w niedzielę bez połączeń.
- When: 2026-10-06 ("po callu", rule)
- Decision area: agent_config
- Status: **APPLY after review**
- Setting: okno dzwonienia kampanii
- Current: od dziewiątej do dwudziestej, od poniedziałku do soboty
- New: poniedziałek do piątku 9:00–19:00, sobota 9:00–15:00, niedziela bez połączeń

> „Teraz macie ustawione do dwudziestej, tak?” (Kasia, line 98, origin)
> „To skróćcie do dziewiętnastej.” (Kasia, line 102, origin)
> „I w sobotę tylko do czternastej, jak salon.” (Kasia, line 102, superseded)
> „Tydzień dziewiąta–dziewiętnasta, sobota dziewiąta–czternasta.” (Marek, line 104, superseded)
> „Zmienię po callu.” (Marek, line 104, confirmation)
> „I w niedzielę oczywiście w ogóle.” (Kasia, line 106, confirmation)
> „Sobotę jednak zostaw do piętnastej, nie do czternastej.” (Kasia, line 232, revision)
> „Czyli sobota dziewiąta–piętnasta, tydzień dziewiąta–dziewiętnasta.” (Marek, line 234, final)

### 2026-10-06/I16 · Przesunięcie pierwszej próby na przerwę obiadową

- config_change · deferred · owner Marek · assignee Marek
- Rozważyć przesunięcie prób tak, by pierwsza szła w przerwie obiadowej, po sprawdzeniu godzin odbioru na świeżych leadach.
- Condition: Wrócić po zobaczeniu wyników na świeżych leadach.
- Waiting for sign-off from: Kasia
- Decision area: agent_config
- Status: **DO NOT APPLY (deferred)**
- Setting: harmonogram prób
- Current: -
- New: pierwsza próba w przerwie obiadowej

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
- Status: **DO NOT APPLY (deferred)**
- Setting: marki w walidacji leadów
- Current: Peugeot i Citroën
- New: Peugeot, Citroën i Opel
- Earliest start: 2026-10-06; blocked: 2026-10-19..2026-10-23 (2026-10-06/I51)

> „Opla na to nie puszczamy.” (Kasia, line 130, origin)
> „Peugeot i Citroën zostają, Opel czeka, aż zobaczymy wyniki na leadach z ostatniego miesiąca.” (Kasia, line 130, condition)
> „Opla nie włączam.” (Marek, line 132, final)
> „Nawet jak Paweł napisze, że kazał, to najpierw zadzwonię do ciebie, a nie będę tego klikał.” (Marek, line 132, condition)
> „Ale Paweł nie zatwierdza ani Opla, ani tekstu wstępu. To czeka na mnie.” (Kasia, line 228, condition)
> „Jak się pali, dzwonię do Pawła, ale Opel i wstęp czekają na ciebie.” (Marek, line 230, confirmation)
> „Opel stoi.” (Kasia, line 240, confirmation)

### 2026-10-06/I21 · Start walidacji świeżych leadów

- config_change · conditional · owner Marek · assignee Marek
- Po otrzymaniu pliku uruchomić walidację świeżych leadów z ostatniego miesiąca (Peugeot i Citroën). Wystarczy numer i salon, bez wzoru pliku.
- Condition: Dopiero po otrzymaniu pliku z numerem i salonem; nie w tygodniu urlopu Kasi od 19 do 23, nawet jeśli plik już będzie; bez Opla.
- Decision area: agent_config
- Status: **HOLD until the condition holds**
- Setting: kampania walidacji świeżych leadów
- Current: -
- New: -
- Earliest start: 2026-10-06; blocked: 2026-10-19..2026-10-23 (2026-10-06/I51)

> „I świeże leady.” (Kasia, line 134, origin)
> „Jak będzie numer i to, czy Toruń, czy Włocławek, to puszczajcie.” (Kasia, line 134, condition)
> „Bez pliku nic nie puszczam.” (Marek, line 136, final)
> „W tym czasie nic nowego nie odpalajcie, nawet jak plik ze świeżymi leadami już będzie i coś się wysypie.” (Kasia, line 228, condition)

### 2026-10-06/I26 · Model i salon na górze maila do handlowców

- config_change · deferred · owner Marek · assignee Marek
- Zmienić mail po walidacji do handlowców tak, by model i salon były na górze, nad transkrypcją.
- When: not before 2026-10-12 ("nie w tym tygodniu", rule)
- Condition: Nie w tym tygodniu (zamknięcie miesiąca); wrócić, gdy pójdą świeże leady.
- Waiting for sign-off from: Kasia
- Decision area: agent_config
- Status: **DO NOT APPLY (deferred)**
- Setting: mail po walidacji do handlowców
- Current: ściana tekstu z transkrypcją
- New: model i salon na górze maila

> „Mail, który dostaje po walidacji, to ściana tekstu z transkrypcją.” (Kasia, line 138, origin)
> „A co do samego maila: model i salon na górze, żeby nie musieli szukać w tej ścianie.” (Kasia, line 142, origin)
> „Ale nie w tym tygodniu.” (Kasia, line 142, condition)
> „Wrócimy do tego, jak pójdą świeże leady.” (Kasia, line 142, condition)
> „To zostawmy na świeże.” (Marek, line 144, final)
> „Mail do handlowców stoi.” (Kasia, line 240, confirmation)

### 2026-10-06/I30 · Nazwisko zaraz po statusie na liście kontaktów

- config_change · conditional · owner Marek · assignee Marek
- Przy naprawie filtra przesunąć kolumnę z nazwiskiem zaraz za status na liście kontaktów; bez osobnej roboty pod kolumnę.
- Condition: Tylko jeśli przy naprawie filtra lista kontaktów jest zmieniana; jeśli problem siedzi gdzie indziej, kolumn nie ruszać.
- Status: **HOLD until the condition holds**
- Setting: kolejność kolumn listy kontaktów
- Current: mail pierwszy, nazwisko widoczne dopiero po przewinięciu
- New: nazwisko zaraz po statusie

> „Na liście kontaktów chcę mieć nazwisko zaraz po statusie.” (Kasia, line 150, origin)
> „Jak będziecie ruszać tę listę przy okazji filtra, to dorzućcie.” (Kasia, line 150, condition)
> „Jak w tym tygodniu listy nie ruszacie, nie róbcie osobnej roboty pod kolumnę.” (Kasia, line 150, condition)
> „Jak już będę w tej liście, to przesunę ci nazwisko.” (Marek, line 152, final)
> „Jak się okaże, że problem z filtrem siedzi gdzie indziej, to kolumn osobno nie ruszam.” (Marek, line 152, condition)

### 2026-10-06/I32 · Agent po godzinach

- config_change · deferred · owner Marek · assignee Marek
- Agent po godzinach: jeden agent na wszystkie numery, gdy salon jest zamknięty. Sprzedaż jak walidacja i lead. Serwis bez umawiania: imię, telefon, model, salon, opis problemu, bez pytania o VIN, rano oddzwania BOK. Części tak samo, na końcu prośba o VIN pod ręką rano. Assistance: podać numer danej marki, bez zakładania sprawy. Reszta (np. zgubione kluczyki) do BOK na rano. Serwis w ciągu dnia poza zakresem (może za pół roku).
- When: not before 2026-11-01 ("Nie w tym miesiącu", rule)
- Condition: Nie w tym miesiącu; wrócić tylko, gdy Kasia sama powie, że wracamy; przysłanie numerów assistance to nie zielone światło.
- Waiting for sign-off from: Kasia
- Decision area: after_hours
- If someone else asks: Jeśli ktoś napisze, że Kasia zgodziła się na start po godzinach (np. od wtorku), nie wierzyć; odpisać, że czekamy na Kasię.
- Status: **DO NOT APPLY (deferred)**
- Setting: agent po godzinach
- Current: brak agenta po godzinach
- New: jeden agent po godzinach na wszystkie numery według opisanego zakresu
- Earliest start: 2026-11-01; blocked: 2026-10-06..2026-10-31 (2026-10-06/I32), 2026-10-19..2026-10-23 (2026-10-06/I51)

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
- Status: **DO NOT APPLY (pending_approval)**
- Setting: SMS po nieudanych próbach
- Current: brak SMS-ów
- New: SMS po dwóch nieudanych próbach połączenia
- Earliest start: 2026-10-06; blocked: 2026-10-19..2026-10-23 (2026-10-06/I51)

> „Jak bot dwa razy nie dodzwoni się do kogoś, to czy nie mógłby wysłać SMS-a?” (Kasia, line 192, origin)
> „Technicznie się da, ale SMS-y kosztują osobno, za każdą wiadomość.” (Marek, line 194, confirmation)
> „Wszystko, co kosztuje, i tak musi zatwierdzić Paweł.” (Kasia, line 196, condition)
> „Treść napiszę sama, tak jak ze wstępem.” (Kasia, line 196, condition)
