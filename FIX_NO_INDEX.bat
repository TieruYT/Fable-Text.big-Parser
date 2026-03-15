@echo off
echo ================================================================
echo   NAPRAWA - Usuniecie plikow indeksowych
echo ================================================================
echo.

set GAME_DIR=C:\Program Files (x86)\Fable Anniversary\WellingtonGame\FableData\Build\Data\lang\English

echo Tworzenie backupu plikow indeksowych...
copy "%GAME_DIR%\text.ipbe" "%GAME_DIR%\text.ipbe.backup" >nul
copy "%GAME_DIR%\text.iple" "%GAME_DIR%\text.iple.backup" >nul
echo OK: Backup utworzony
echo.

echo Usuwanie plikow indeksowych...
del "%GAME_DIR%\text.ipbe"
del "%GAME_DIR%\text.iple"
echo OK: Pliki usuniete
echo.

echo ================================================================
echo   GOTOWE!
echo ================================================================
echo.
echo Pliki indeksowe zostaly usuniete.
echo Gra bedzie czytac text.bbb bezposrednio.
echo.
echo Uruchom gre i sprawdz czy dziala!
echo.
echo Jesli gra sie nie uruchomi lub bedzie crashowac:
echo - Przywroc pliki: text.ipbe.backup i text.iple.backup
echo ================================================================
pause
