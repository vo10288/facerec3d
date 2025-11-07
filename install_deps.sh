#!/bin/bash

# Script di installazione dipendenze per Comparatore Biometrico Volti 3D

echo "=================================="
echo "Comparatore Biometrico Volti 3D"
echo "Installazione dipendenze"
echo "=================================="
echo ""

# Controlla se Python è installato
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 non trovato. Installalo prima di continuare."
    exit 1
fi

echo "✅ Python3 trovato: $(python3 --version)"
echo ""

# Installa le dipendenze
echo "📦 Installazione dipendenze..."
echo ""

pip3 install --upgrade pip

echo "Installazione opencv-python..."
pip3 install opencv-python

echo "Installazione mediapipe..."
pip3 install mediapipe

echo "Installazione pillow..."
pip3 install pillow

echo "Installazione numpy..."
pip3 install numpy

echo ""
echo "=================================="
echo "✅ Installazione completata!"
echo "=================================="
echo ""
echo "Per avviare l'applicazione:"
echo "  python3 comparatore_volti_gui.py"
echo ""
