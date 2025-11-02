@echo off
REM Geo-Verified Proxy Testing for Windows

echo ==========================================
echo Geo-Verified Proxy Testing
echo ==========================================
echo.

if "%1"=="" (
    echo Using default countries: RU,CN,IR,UK,HK,SG
    echo.
    echo To test other countries, use:
    echo   test_proxy_geo.bat US,UK,CA
    echo.
    python test_proxy_geo.py
) else (
    echo Testing countries: %1
    echo.
    python test_proxy_geo.py %1
)

echo.
pause
