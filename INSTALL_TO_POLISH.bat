@echo off
echo ================================================================
echo   INSTALATOR - KATALOG POLISH (PRAWIDLOWY!)
echo ================================================================
echo.

set GAME_POLISH=C:\Program Files (x86)\Fable Anniversary\WellingtonGame\FableData\Build\Data\lang\Polish
set GAME_ENGLISH=C:\Program Files (x86)\Fable Anniversary\WellingtonGame\FableData\Build\Data\lang\English
set POLISH_FILE=polish_text_exact.bbb

echo Gra prawdopodobnie korzysta z katalogu "Polish" gdy wybierzesz polski jezyk!
echo Musimy skopiowac spolszczenie tam, a nie do "English".
echo.

if not exist "%POLISH_FILE%" (
    echo BLAD: Nie znaleziono %POLISH_FILE%
    pause
    exit /b 1
)

REM Sprawdź czy katalogi istnieją
if not exist "%GAME_POLISH%" (
    echo BLAD: Nie znaleziono katalogu Polish w grze
    pause
    exit /b 1
)

echo Katalog docelowy: %GAME_POLISH%
echo.

REM Backup
echo [1/3] Tworzenie backupu...
if not exist "%GAME_POLISH%\text.bbb.backup" (
    copy "%GAME_POLISH%\text.bbb" "%GAME_POLISH%\text.bbb.backup" >nul
    echo   - OK: Backup utworzony
) else (
    echo   - Backup juz istnieje
)
echo.

REM Instalacja do POLISH
echo [2/3] Instalowanie do katalogu Polish...
copy "%POLISH_FILE%" "%GAME_POLISH%\text.bbb" >nul
if errorlevel 1 (
    echo   - BLAD! Uruchom jako administrator
    pause
    exit /b 1
)
echo   - OK: Skopiowano do Polish/text.bbb
echo.

REM Opcjonalnie - też do English (na wszelki wypadek)
echo [3/3] Kopiowanie rowniez do English (backup)...
if not exist "%GAME_ENGLISH%\text.bbb.backup" (
    copy "%GAME_ENGLISH%\text.bbb" "%GAME_ENGLISH%\text.bbb.backup" >nul
)
copy "%POLISH_FILE%" "%GAME_ENGLISH%\text.bbb" >nul
echo   - OK: Skopiowano rowniez do English/text.bbb
echo.

echo ================================================================
echo   INSTALACJA ZAKONCZONA!
echo ================================================================
echo.
echo Spolszczenie zainstalowane w katalogu Polish i English.
echo.
echo KOLEJNE KROKI:
echo 1. Uruchom gre
echo 2. W ustawieniach wybierz jezyk: POLISH (Polski)
echo    (lub jesli nie ma takiej opcji, zostaw English)
echo 3. Zrestartuj gre jesli to konieczne
echo 4. Sprawdz czy teksty sa po polsku!
echo.
echo UWAGA: Jesli w ustawieniach nie ma "Polish":
echo - Gra bedzie korzystac z English/text.bbb (tez spolszczony)
echo - Albo zmien jezyk Steam na Polski przed uruchomieniem gry
echo.
echo ================================================================
pause
