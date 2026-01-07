#!/bin/bash

# Automated OpenCV 4.11.0 Installation Script for Jetson Orin Nano
# JetPack 6.0/6.1 (Ubuntu 22.04)
# CUDA-enabled build with jtop installation

set -e  # Exit on error

OPENCV_VERSION="4.11.0"
INSTALL_DIR="/usr"
BUILD_CORES=$(nproc)
CUDA_ARCH="8.7"  # Orin Nano Ampere architecture

echo "=========================================="
echo "OpenCV ${OPENCV_VERSION} Automated Installer"
echo "Target: Jetson Orin Nano (JetPack 6.x)"
echo "=========================================="

# Function to check command success
check_status() {
    if [ $? -eq 0 ]; then
        echo "[SUCCESS] $1"
    else
        echo "[ERROR] $1 failed"
        exit 1
    fi
}

# Clean previous installations
echo "[1/10] Cleaning previous OpenCV installations..."
sudo apt-get purge -y libopencv* python3-opencv opencv-python || true
sudo apt-get autoremove -y
sudo apt-get autoclean

# Update system
echo "[2/10] Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y
check_status "System update"

# Install dependencies
echo "[3/10] Installing dependencies..."
sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    unzip \
    pkg-config \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libgtk2.0-dev \
    libgtk-3-dev \
    libcanberra-gtk-module \
    python3-dev \
    python3-numpy \
    python3-pip \
    libxvidcore-dev \
    libx264-dev \
    libtbb2 \
    libtbb-dev \
    libdc1394-dev \
    libv4l-dev \
    v4l-utils \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-good1.0-dev \
    libavresample-dev \
    libvorbis-dev \
    libxine2-dev \
    libfaac-dev \
    libmp3lame-dev \
    libtheora-dev \
    libopencore-amrnb-dev \
    libopencore-amrwb-dev \
    libopenblas-dev \
    libatlas-base-dev \
    libblas-dev \
    liblapack-dev \
    libeigen3-dev \
    gfortran \
    libhdf5-dev \
    protobuf-compiler \
    libprotobuf-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libtesseract-dev \
    libleptonica-dev

check_status "Dependencies installation"

# Clean workspace
echo "[4/10] Preparing workspace..."
cd ~
rm -rf opencv_build
mkdir opencv_build
cd opencv_build

# Download OpenCV
echo "[5/10] Downloading OpenCV ${OPENCV_VERSION}..."
wget -q -O opencv.zip https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip
wget -q -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/${OPENCV_VERSION}.zip
check_status "OpenCV download"

# Extract archives
echo "[6/10] Extracting archives..."
unzip -q opencv.zip
unzip -q opencv_contrib.zip
rm opencv.zip opencv_contrib.zip
mv opencv-${OPENCV_VERSION} opencv
mv opencv_contrib-${OPENCV_VERSION} opencv_contrib

# Create build directory
cd opencv
mkdir build
cd build

# Configure CMake
echo "[7/10] Configuring CMake with CUDA support..."
cmake -D CMAKE_BUILD_TYPE=RELEASE \
      -D CMAKE_INSTALL_PREFIX=${INSTALL_DIR} \
      -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
      -D EIGEN_INCLUDE_PATH=/usr/include/eigen3 \
      -D WITH_OPENCL=OFF \
      -D WITH_CUDA=ON \
      -D CUDA_ARCH_BIN=${CUDA_ARCH} \
      -D CUDA_ARCH_PTX="" \
      -D WITH_CUDNN=ON \
      -D WITH_CUBLAS=ON \
      -D ENABLE_FAST_MATH=ON \
      -D CUDA_FAST_MATH=ON \
      -D OPENCV_DNN_CUDA=ON \
      -D ENABLE_NEON=ON \
      -D WITH_QT=OFF \
      -D WITH_OPENMP=ON \
      -D WITH_OPENGL=ON \
      -D BUILD_TIFF=ON \
      -D WITH_FFMPEG=ON \
      -D WITH_GSTREAMER=ON \
      -D WITH_TBB=ON \
      -D BUILD_TBB=ON \
      -D BUILD_TESTS=OFF \
      -D WITH_EIGEN=ON \
      -D WITH_V4L=ON \
      -D WITH_LIBV4L=ON \
      -D OPENCV_ENABLE_NONFREE=ON \
      -D INSTALL_C_EXAMPLES=OFF \
      -D INSTALL_PYTHON_EXAMPLES=OFF \
      -D PYTHON3_PACKAGES_PATH=/usr/lib/python3/dist-packages \
      -D OPENCV_GENERATE_PKGCONFIG=ON \
      -D BUILD_EXAMPLES=OFF ..

check_status "CMake configuration"

# Build OpenCV
echo "[8/10] Building OpenCV (this will take 2-3 hours)..."
echo "Using ${BUILD_CORES} CPU cores for compilation"
make -j${BUILD_CORES}
check_status "OpenCV build"

# Install OpenCV
echo "[9/10] Installing OpenCV..."
sudo make install
sudo ldconfig
check_status "OpenCV installation"

# Verify installation
echo "Verifying OpenCV installation..."
python3 -c "import cv2; print(f'OpenCV {cv2.__version__} installed'); print(f'CUDA: {cv2.cuda.getCudaEnabledDeviceCount() > 0}')"
check_status "OpenCV verification"

# Install jtop
echo "[10/10] Installing jtop..."
sudo pip3 install -U jetson-stats
check_status "jtop installation"

# Clean build files
echo "Cleaning build files..."
cd ~
rm -rf opencv_build

echo "=========================================="
echo "Installation Complete!"
echo "OpenCV ${OPENCV_VERSION} with CUDA support installed"
echo "jtop installed"
echo "=========================================="
echo ""
echo "System will reboot in 10 seconds..."
echo "Press Ctrl+C to cancel reboot"
sleep 10

sudo reboot