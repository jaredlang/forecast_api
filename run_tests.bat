@echo off
REM Test runner script for Weather Forecast API (Windows)

setlocal enabledelayedexpansion

echo ========================================
echo Weather Forecast API - Test Runner
echo ========================================
echo.

set TEST_TYPE=%1
if "%TEST_TYPE%"=="" set TEST_TYPE=all

if "%TEST_TYPE%"=="unit" goto UNIT
if "%TEST_TYPE%"=="pytest" goto UNIT
if "%TEST_TYPE%"=="weather" goto WEATHER
if "%TEST_TYPE%"=="stats" goto STATS
if "%TEST_TYPE%"=="health" goto HEALTH
if "%TEST_TYPE%"=="manual" goto MANUAL
if "%TEST_TYPE%"=="coverage" goto COVERAGE
if "%TEST_TYPE%"=="all" goto ALL
goto USAGE

:UNIT
echo ^=^=^> Running unit tests with pytest...
pytest -v
if errorlevel 1 goto ERROR
echo [32m✓ Unit tests completed![0m
goto END

:WEATHER
echo ^=^=^> Running weather endpoint tests...
pytest tests/test_weather.py -v
if errorlevel 1 goto ERROR
echo [32m✓ Weather tests completed![0m
goto END

:STATS
echo ^=^=^> Running stats endpoint tests...
pytest tests/test_stats.py -v
if errorlevel 1 goto ERROR
echo [32m✓ Stats tests completed![0m
goto END

:HEALTH
echo ^=^=^> Running health endpoint tests...
pytest tests/test_health.py -v
if errorlevel 1 goto ERROR
echo [32m✓ Health tests completed![0m
goto END

:MANUAL
set API_URL=%2
if "%API_URL%"=="" set API_URL=http://localhost:8000
echo ^=^=^> Running manual integration tests against %API_URL%...
echo [33m! Make sure the API server is running![0m
python tests/manual_test.py %API_URL%
if errorlevel 1 goto ERROR
goto END

:COVERAGE
echo ^=^=^> Running tests with coverage report...
pytest --cov=. --cov-report=html --cov-report=term
if errorlevel 1 goto ERROR
echo [32m✓ Coverage report generated in htmlcov/[0m
goto END

:ALL
echo ^=^=^> Running all unit tests...
pytest -v
if errorlevel 1 goto ERROR
echo [32m✓ All unit tests completed![0m
echo.
echo [33m! To run manual integration tests, use: run_tests.bat manual[0m
goto END

:USAGE
echo Usage: run_tests.bat [test_type] [options]
echo.
echo Test types:
echo   all         - Run all unit tests (default)
echo   unit^|pytest - Run all unit tests
echo   weather     - Run weather endpoint tests only
echo   stats       - Run stats endpoint tests only
echo   health      - Run health endpoint tests only
echo   manual [url] - Run manual integration tests (requires running server)
echo   coverage    - Run tests with coverage report
echo.
echo Examples:
echo   run_tests.bat
echo   run_tests.bat unit
echo   run_tests.bat weather
echo   run_tests.bat manual http://localhost:8000
echo   run_tests.bat coverage
exit /b 1

:ERROR
echo.
echo [31mTests failed![0m
exit /b 1

:END
echo.
echo ========================================
echo Tests completed successfully!
echo ========================================
