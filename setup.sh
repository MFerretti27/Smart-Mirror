#!/usr/bin/env bash

# To change what weather data is displayed, visit: https://open-meteo.com/en/docs

# To learn specific camera configuration, visit:
# https://docs.arducam.com/Raspberry-Pi-Camera/Native-camera/16MP-IMX519/#step-4-modify-config-file


set -e

echo "=== Smart Mirror Setup Script ==="

# Update system
sudo apt update
sudo apt upgrade -y

echo "=== Installing system dependencies ==="
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    libqt5gui5 \
    libopenexr-dev \
    libilmbase-dev \
    libgtk-3-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libhdf5-103 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libtbb2 \
    libtbb-dev \
    libdc1394-22-dev \
    libv4l-dev \
    v4l-utils \
    cmake \
    gfortran \
    pkg-config \
    rpicam-apps \
    python3-opencv \
    opencv-data

echo "=== Installing Python packages ==="
pip3 install --upgrade pip wheel setuptools

# Install needed Python libraries
pip3 install \
    FreeSimpleGUI \
    numpy \
    requests \
    pytz \
    opencv-contrib-python \
    opencv-python \
    pillow \
    mypy

echo "=== Verifying installation ==="

# Check rpicam
if ! command -v rpicam-still &>/dev/null; then
    echo "❌ rpicam-still not found. Please make sure you are on Raspberry Pi OS Bookworm or Bullseye with libcamera support."
    exit 1
else
    echo "✅ rpicam-still installed"
fi

# Check OpenCV
python3 - <<'EOF'
import cv2, numpy
print("✅ OpenCV version:", cv2.__version__)
if not hasattr(cv2, "face"):
    print("❌ cv2.face is missing. Make sure opencv-contrib-python installed correctly.")
else:
    print("✅ cv2.face module available")
EOF

echo "=== Setup complete! ==="
echo "Now run: python3 smart_mirror.py"
