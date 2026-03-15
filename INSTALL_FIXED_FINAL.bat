@echo off
echo ================================================================
echo   INSTALATOR - WERSJA NAPRAWIONA (FINAL)
echo ================================================================
echo.

set GAME_POLISH=C:\Program Files (x86)\Fable Anniversary\WellingtonGame\FableData\Build\Data\lang\Polish
set GAME_ENGLISH=C:\Program Files (x86)\Fable Anniversary\WellingtonGame\FableData\Build\Data\lang\English
set POLISH_FILE=polish_text_FIXED.bbb

if not exist "%POLISH_FILE%" (
    echo BLAD: Nie znaleziono %POLISH_FILE%
    pause
    exit /b 1
)

echo Ta wersja jest NAPRAWIONA:
echo - Zachowuje nazwy ASCII (TEXT_GUI_*)
echo - Zamienia TYLKO tresci na polskie
echo - Powinno dzialac w grze!
echo.
pause
echo.

REM Backup Polish
if not exist "%GAME_POLISH%\text.bbb.backup" (
    copy "%GAME_POLISH%\text.bbb" "%GAME_POLISH%\text.bbb.backup" >nul 2>&1
)

REM Backup English
if not exist "%GAME_ENGLISH%\text.bbb.backup" (
    copy "%GAME_ENGLISH%\text.bbb" "%GAME_ENGLISH%\text.bbb.backup" >nul 2>&1
)

echo [1/2] Instalowanie do Polish...
copy "%POLISH_FILE%" "%GAME_POLISH%\text.bbb" >nul
if errorlevel 1 (
    echo   - BLAD! Uruchom jako administrator
    pause
    exit /b 1
)
echo   - OK

echo [2/2] Instalowanie do English...
copy "%POLISH_FILE%" "%GAME_ENGLISH%\text.bbb" >nul
echo   - OK
echo.

echo ================================================================
echo   INSTALACJA ZAKONCZONA!
echo ================================================================
echo.
echo Spolszczenie zainstalowane do Polish i English.
echo.
echo URUCHOM GRE I SPRAWDZ!
echo.
echo Jesli nadal nie dziala:
echo - Sprawdz czy teksty sa polskie w naszym pliku
echo - Moze byc problem z fontami (ogonkami)
echo.
echo ================================================================
pause
