@echo off
echo ================================================================
echo   INSTALATOR SPOLSZCZENIA - WERSJA FIXED
echo   (Zachowuje offsety - dziala z indeksami)
echo ================================================================
echo.

set GAME_DIR=C:\Program Files (x86)\Fable Anniversary\WellingtonGame\FableData\Build\Data\lang\English
set POLISH_FILE=polish_text_exact.bbb

if not exist "%POLISH_FILE%" (
    echo BLAD: Nie znaleziono %POLISH_FILE%
    pause
    exit /b 1
)

if not exist "%GAME_DIR%" (
    echo BLAD: Nie znaleziono katalogu gry
    pause
    exit /b 1
)

echo Katalog gry: %GAME_DIR%
echo.

REM Backup
echo [1/2] Backup...
if not exist "%GAME_DIR%\text.bbb.backup" (
    copy "%GAME_DIR%\text.bbb" "%GAME_DIR%\text.bbb.backup" >nul
    echo   - OK: text.bbb.backup utworzony
) else (
    echo   - Backup juz istnieje
)
echo.

REM Instalacja
echo [2/2] Instalowanie spolszczenia...
copy "%POLISH_FILE%" "%GAME_DIR%\text.bbb" >nul
if errorlevel 1 (
    echo   - BLAD! Uruchom jako administrator
    pause
    exit /b 1
)

echo   - OK: Spolszczenie zainstalowane
echo.

echo ================================================================
echo   INSTALACJA ZAKONCZONA!
echo ================================================================
echo.
echo Spolszczenie z zachowanymi offsetami zainstalowane.
echo Pliki indeksowe (.ipbe/.iple) nie wymagaja zmiany.
echo.
echo UWAGA: Niektore dlugie teksty moga byc obciete.
echo To normalne - offsety musza sie zgadzac.
echo.
echo Mozesz teraz uruchomic gre!
echo ================================================================
pause
