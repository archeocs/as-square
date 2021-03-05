# AS-SQUARE Podręcznik użytkownika

`AS-SQUARE` to wtyczka do programu [QGIS](https://qgis.org), która wspomaga
użytkowników w zapisywaniu wyników archeologiczne prospekcji terenowej.
Dane zapisywane są w przestrzennej bazie danych zgodnie z metodą Kwadratów 
analitycznych.

Informacje zapisane w przestrzennej bazie danych [Spatialite](https://www.gaia-gis.it/fossil/libspatialite/home) wczytane 
w QGIS jako warstwa wektorowa mogą być wykorzystane do analiz przestrzennych.

## Instalacja

Wtyczkę `AS-SQUARE` można zainstalować przy pomocy mechanizmu obsługi wtyczek, 
który jest wbudowany w programie QGIS. Aplikacja umożliwia użytkownikom pobieranie i
instalowanie rozszerzeń z tak zwanych _repozytoriów_.

Przed instalacją wtyczki `AS-SQUARE` konieczne jest podanie adresu repozytorium, 
z którego QGIS pobiera pliki niezbędne do instalacji albo aktualizacji do najnowszej 
wersji.

Repozytorium `AS-SQUARE` znajduje się pod adresem **https://github.com/archeocs/as-square/releases/latest/download/plugins.xml**

### Dodawanie repozytorium w programie QGIS

1. Z menu `Wtyczki` wybierz `Zarządzanie wtyczkami...`.
![Repozytorium 1](1_Instalacja_repozytorium_1.png)
2. Po lewej stronie okna wybierz sekcję `Ustawienia`.
3. Przewiń suwakiem z prawej strony do momentu aż będzie widoczna sekcja `Repozytoria wtyczek`.
![Repozytorium 1](1_Instalacja_repozytorium_2.png)
4. Kliknij przycisk `Dodaj`.
5. W polu `Name` podaj dowolną nazwę repozytorium. Na przykład `wtyczka as-square`.
6. W polu `URL` wpisz adres repozytorium **https://github.com/archeocs/as-square/releases/latest/download/plugins.xml**
![Repozytorium 1](1_Instalacja_repozytorium_3.png)
7. Naciśnij przycisk `OK`.
8. Naciśnij przycisk `Wczytaj ponownie zawartość repozytoriów`.
9. Naciśnij przycisk `Zamknij`.

Po konifiguracji repozytorium wtyczka `AS-SQUARE` powinna zostać wyświetlona na 
liście gotowych do instalacji. 

### Instalacja wtyczki

1. Z menu `Wtyczki` wybierz `Zarządzanie wtyczkami...`.
2. Po lewej stronie okna wybierz sekcję `Wszystkie`.
3. W polu tekstowym z lupą na górze okna wpisz `as-square`
![Repozytorium 1](1_Instalacja_instalacja_1.png)
4. Zaznacz wtyczkę `as-square`.
5. Kliknij przycisk `Zainstaluj wtyczkę`.
6. Po lewej stronie okna wybierz sekcję `Zainstalowane`.
7. Upewnij się, że wtyczka `as-square` znajduje się na liście i jest zaznaczona
![Repozytorium 1](1_Instalacja_instalacja_2.png)
8. Kliknij przycisk `Zamknij`.
9. Wyłącz program QGIS i uruchom ponownie.
10. Upewnij się, że przycisk `as-square` jest widoczny na pasku narzędzi na górze głównego 
   okna programu.
   
## Baza danych

Działanie wtyczki polega na zapisywaniu danych w przestrzennej bazie danych. Wtyczka jest
dostosowana do pracy z bazą [Spatialite](https://www.gaia-gis.it/fossil/libspatialite/home).
Każdorazowo przed rozpoczęciem pracy z wtyczką `AS-SQUARE` konieczne jest wczytanie z 
przestrzennej bazy danych odpowiedniej warstwy wektorowej o nazwie `AS_RECORDS`. 

Bazę danych z warstwą `AS_RECORDS` można pobrać 
[klikając na link](https://github.com/archeocs/as-square/releases/latest/download/empty-db.zip) 

Praca metodą kwadratów analitycznych polega na dodawaniu informacji archeologicznych dla
kwadratów o krawędzi 10 metrów lub 50 metrów, na które dzieli się obszar podlegający badaniom. 

1. Siatka kwadratów powinna zostać zapisana w warstwie wektorowej o nazwie:

* `GRID_10_M` dla siatki z kwadratami 10 metrów
* `GRID_50_M` dla siatki z kwadratami 50 metrów

2. Warstwa wektorowa powinna posiadać następujące atrybuty:

* `SQUARE_ID` - unikatowy identyfikator kwadratu w ramach siatki
* `GEOMETRY` - współrzędne geograficzne
* `SQUARE_DIMENSION` - zawiera stałą wartość: 50 dla warstwy `GRID_50_M` albo 10 dla `GRID_10_M`

![Baza danych](3_Baza_danych_warstwy.png)

## Aktualizacja

Aktualizacje wtyczki `AS-SQUARE` uzupełniają jej funkcje o nowe możliwości oraz naprawiają 
odkryte błędy. Użytkownik powinien regularnie sprawdzać najnowszą wersję programu. 

### Sprawdzanie wersji wtyczki

1. Z menu `Wtyczki` wybierz `Zarządzanie wtyczkami...`.
2. Po lewej stronie okna wybierz sekcję `Wszystkie`.
3. W polu tekstowym z lupą na górze okna wpisz `as-square`
![Repozytorium 1](2_Aktualizacja_nowa_wersja.png)
4. Zaznacz wtyczkę `as-square`.
5. W panelu po prawej porównaj wartości `Zainstalowana wersja` oraz `Dostępna wersja`.

### Aktualizacja wtyczki

1. Z menu `Wtyczki` wybierz `Zarządzanie wtyczkami...`.
2. Po lewej stronie okna wybierz sekcję `Wszystkie`.
3. W polu tekstowym z lupą na górze okna wpisz `as-square`
![Repozytorium 1](2_Aktualizacja_nowa_wersja.png)
4. Zaznacz `as-square` jeżeli jest widoczna na liście.
5. Kliknij przycisk `Aktualizuj wtyczkę`.

Po aktualizacji wtyczka może wymagać zmian w bazie danych, bez których nie będzie działała 
prawidłowo. Po każdej aktualizacji użytkownik powinien sprawdzić, czy wprowadzenie zmian 
jest konieczne. Wtyczka `AS-SQUARE` udostępnia użytkownikom funkcje do sprawdzania wersji 
bazy danych oraz wprowadzania koniecznych zmian.

### Sprawdzanie wersji bazy danych

1. Sprawdź, czy baza jest widoczna w panelu `Przeglądarka`.
![Migracja](2_Aktualizacja_migracja_db_1.png)
2. Z menu `Wtyczki` wybierz `as-square` a następnie `Sprawdź bazę danych`.
3. Z rozwijanej listy wybierz bazę, która powinna zostać sprawdzona.
![Migracja](2_Aktualizacja_migracja_db_2.png)
4. Kliknij przycisk `OK`.
5. Na górze ekranu pojawi się komunikat `Wykonaj migrację` należy przeprowadzić 
 migrację bazy.
 ![Migracja](2_Aktualizacja_migracja_db_3.png)
6. Jeżeli komunikat mówi `Baza jest aktualna` to znaczy, że migrania nie jest 
konieczna.
![Migracja](2_Aktualizacja_migracja_db_4.png)

### Migracja bazy danych

**UWAGA! Przed migracją bazy danych należy wykonać kopię bezpieczeństwa bazy!
Skopiuj plik bazy danych do innego katalogu. W przypadku niepowodzenia migracji
będziesz mógł go wykorzystać do przywrócenia poprzedniej wersji bazy**

1. Sprawdź, czy baza jest widoczna w panelu `Przeglądarka`.
2. Z menu `Wtyczki` wybierz `as-square` a następnie `Migruj bazę danych`.
3. Z rozwijanej listy wybierz bazę, która powinna zostać zaktualizowana.
4. Kliknij przycisk `OK`.
5. Jeżeli migracja zakończyła się powodzeniem, zostanie wyświetlony komunikat 
`Migracja zakończona sukcesem`.
![Migracja](2_Aktualizacja_migracja_db_sukces.png)

## Pierwsze użycie

[TBD]

## Dodawanie informacji

[TBD]

## Aktualizacja informacji
 
[TBD]
