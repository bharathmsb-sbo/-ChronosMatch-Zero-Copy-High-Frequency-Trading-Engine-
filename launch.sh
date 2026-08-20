#!/bin/bash
# ChronosMatch Launch Script
# This script sets up and launches all components of the trading engine

echo "=========================================="
echo "  ChronosMatch - HFT Trading Engine"
echo "=========================================="

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Build Cython extension
echo "Building Cython extension..."
python setup.py build_ext --inplace

# Initialize ring buffer if it doesn't exist
if [ ! -f "chronos_mmap.bin" ]; then
    echo "Initializing ring buffer..."
    python -c "from ring_buffer import RingBuffer; rb = RingBuffer(); rb.create(); rb.close()"
fi

echo ""
echo "Setup complete! Launch components in separate terminals:"
echo ""
echo "Terminal 1 - Matching Engine:"
echo "  python matching_engine.py"
echo ""
echo "Terminal 2 - Market Simulator:"
echo "  python market_simulator.py"
echo ""
echo "Terminal 3 - Dashboard:"
echo "  python dashboard.py"
echo ""
echo "Press Ctrl+C in any terminal to stop that component"
