@echo off
REM ChronosMatch Launch Script for Windows
REM This script sets up and launches all components of the trading engine

echo ==========================================
echo   ChronosMatch - HFT Trading Engine
echo ==========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Build Cython extension
echo Building Cython extension...
python setup.py build_ext --inplace

REM Initialize ring buffer if it doesn't exist
if not exist "chronos_mmap.bin" (
    echo Initializing ring buffer...
    python -c "from ring_buffer import RingBuffer; rb = RingBuffer(); rb.create(); rb.close()"
)

echo.
echo Setup complete! Launch components in separate terminals:
echo.
echo Terminal 1 - Matching Engine:
echo   python matching_engine.py
echo.
echo Terminal 2 - Market Simulator:
echo   python market_simulator.py
echo.
echo Terminal 3 - Dashboard:
echo   python dashboard.py
echo.
echo Press Ctrl+C in any terminal to stop that component
pause
