# Dev tickets

### 2026-10-06/I05 · Agent drugi raz pyta o model

- bug · blocked · owner Marek · assignee Marek
- Zbadać rozmowę, w której asystentka przestała reagować na klientkę i drugi raz zapytała o model.
- Condition: Potrzebny numer albo nagranie tej rozmowy; Ola go nie podała.
- Reported: Ola zgłosiła wczoraj dwie takie sytuacje, bez numerów (date 2026-10-05) [to verify in other]

> „W drugiej asystentka w środku rozmowy przestała odpowiadać na to, co klientka mówi, i drugi raz zapytała o model.” (Kasia, line 38, origin)
> „Żadnego. Ola nie spisała numerów, powiedziała tylko „jakaś pani przed południem”.” (Kasia, line 42, condition)
> „A tej drugiej sytuacji, gdzie pyta drugi raz o model, bez nagrania nie znajdę. Ola nie dała numeru.” (Marek, line 60, final)

### 2026-10-06/I09 · Drugi telefon tego samego dnia po rozłączeniu w ciągu 3 sekund

- bug · open · owner Marek · assignee Marek
- Sprawdzić na tej kampanii, dlaczego agent dzwonił drugi raz tego samego dnia do osób, które rozłączyły się w ciągu 3 sekund, mimo ustawionej reguły.
- When: 2026-10-06 ("zaraz po rozmowie", rule)
- Reported: Skonfigurowano brak drugiej próby tego samego dnia po rozłączeniu w ciągu 3 sekund [to verify in config]
- Reported: Agent mimo to zadzwonił drugi raz (date 2026-10-05) [to verify in call_log]
- Reported: Sześć przypadków na tej samej kampanii po południu [to verify in call_log]
- Reported: Pierwszy przypadek o 16:40, numer kończący się na 14, dwie próby jedna po drugiej [to verify in call_log]

> „Ustawialiśmy, że jak ktoś się rozłączy w ciągu trzech sekund, to agent nie dzwoni do niego drugi raz tego samego dnia.” (Kasia, line 90, origin)
> „Wczoraj i tak zadzwonił.” (Kasia, line 90, origin)
> „Dobra, sprawdzę po spotkaniu na tej kampanii, nie będziemy teraz w tym grzebać.” (Marek, line 92, confirmation)
> „wy zerkacie na ten drugi telefon po rozłączeniu, bo miał nie iść, a poszedł.” (Kasia, line 240, confirmation)
> „Drugi telefon i filtr biorę zaraz po rozmowie, adres i godziny dzisiaj.” (Marek, line 242, final)

### 2026-10-06/I25 · Rozmowa o przeglądzie oznaczona jako lead sprzedażowy

- bug · blocked · owner Marek · assignee Marek
- Sprawdzić, czy agent źle zakwalifikował rozmowę o przeglądzie jako lead sprzedażowy, czy handlowiec nie doczytał maila.
- Condition: Dopiero po wiadomości od Kasi z tą sprawą; nie zgadywać, która to kampania.
- If someone else asks: Nie szukać sprawy na własną rękę ani przez Olę; czekać na wiadomość od Kasi.
- Reported: Handlowiec dostał mail, w którym klient chciał umówić przegląd (date 2026-10-05) [to verify in other]

> „A u niej w systemie wpadło to jako lead sprzedażowy.” (Kasia, line 138, origin)
> „Jak nie, to nie zgadujcie, która to kampania.” (Kasia, line 138, condition)
> „Jak mi tego nie prześlesz, to nie wiem, czy agent źle to zakwalifikował, czy ona nie doczytała.” (Marek, line 140, final)
> „Bez tego nie ruszam.” (Marek, line 140, final)
> „A tego przeglądu, co Ola ma w skrzynce, nie ruszajcie bez wiadomości ode mnie.” (Kasia, line 240, condition)

### 2026-10-06/I28 · Filtr statusu „zainteresowany” nie zawęża listy

- bug · open · owner Marek · assignee Marek
- Sprawdzić, dlaczego filtr statusu „zainteresowany” na liście kontaktów nie zawęża wyników (filtr daty działa).
- When: 2026-10-06 ("zaraz po rozmowie", rule)
- Reported: Filtr daty na liście działa (date 2026-10-05) [to verify in other]

> „Na liście kontaktów filtr „zainteresowany” też nie zawęża.” (Kasia, line 146, origin)
> „Widzę: data działa, a filtr statusu nie.” (Marek, line 148, confirmation)
> „To sprawdzę u nas po callu.” (Marek, line 148, confirmation)
> „I na filtr, bo „zainteresowany” nie zawęża listy.” (Kasia, line 240, confirmation)
> „Drugi telefon i filtr biorę zaraz po rozmowie, adres i godziny dzisiaj.” (Marek, line 242, final)
