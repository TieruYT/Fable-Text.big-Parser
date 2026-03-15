@echo off
echo ================================================================
echo   INSTALATOR POLSKIEGO SPOLSZCZENIA
echo   Fable Anniversary - Polish Translation
echo ================================================================
echo.

REM Ustaw ścieżki
set GAME_DIR=C:\Program Files (x86)\Fable Anniversary\WellingtonGame\FableData\Build\Data\lang\English
set POLISH_FILE=polish_text.bbb

REM Sprawdź czy plik istnieje
if not exist "%POLISH_FILE%" (
    echo BLAD: Nie znaleziono pliku %POLISH_FILE%
    echo Upewnij sie ze uruchamiasz z katalogu ze spolszczeniem
    pause
    exit /b 1
)

REM Sprawdź czy katalog gry istnieje
if not exist "%GAME_DIR%" (
    echo BLAD: Nie znaleziono katalogu gry
    echo Sprawdz sciezke: %GAME_DIR%
    pause
    exit /b 1
)

echo.
echo Katalog gry: %GAME_DIR%
echo.

REM Backup
echo [1/3] Tworzenie kopii zapasowej...

if exist "%GAME_DIR%\text.bbb.backup" (
    echo   - Backup juz istnieje, pomijam
) else (
    copy "%GAME_DIR%\text.bbb" "%GAME_DIR%\text.bbb.backup" >nul
    if errorlevel 1 (
        echo   - BLAD: Nie mozna utworzyc backupu
        echo   - Uruchom jako administrator!
        pause
        exit /b 1
    )
    echo   - OK: Utworzono text.bbb.backup
)

echo.
echo [2/3] Instalowanie polskiego spolszczenia...

copy "%POLISH_FILE%" "%GAME_DIR%\text.bbb" >nul
if errorlevel 1 (
    echo   - BLAD: Nie mozna skopiowac pliku
    echo   - Upewnij sie ze gra jest wylaczona
    echo   - Uruchom jako administrator
    pause
    exit /b 1
)

echo   - OK: Skopiowano polish_text.bbb
echo.

echo [3/3] Weryfikacja...
if exist "%GAME_DIR%\text.bbb" (
    echo   - OK: Plik zainstalowany poprawnie
) else (
    echo   - BLAD: Cos poszlo nie tak
    pause
    exit /b 1
)

echo.
echo ================================================================
echo   INSTALACJA ZAKONCZONA!
echo ================================================================
echo.
echo Spolszczenie zainstalowane pomyslnie!
echo.
echo Mozesz teraz uruchomic gre.
echo.
echo UWAGA: Jesli spolszczenie nie dziala:
echo 1. Sprawdz czy gra ma polskie czcionki (ogonki)
echo 2. Przywroc backup: text.bbb.backup -^> text.bbb
echo.
echo ================================================================
pause
