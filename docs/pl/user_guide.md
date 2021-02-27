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

## Aktualizacja

[TBD]

## Uruchomienie

[TBD]

## Dodawanie informacji

[TBD]

## Aktualizacja informacji
 
[TBD]
