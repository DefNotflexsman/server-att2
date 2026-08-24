#!/bin/bash

# 1. Download and Install Miniconda if conda command is missing
if ! command -v conda &> /dev/null
then
    echo "Conda not found. Downloading Miniconda for macOS Apple Silicon..."
    curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
    
    echo "Installing Miniconda..."
    bash Miniconda3-latest-MacOSX-arm64.sh -b -p $HOME/miniconda
    
    # Initialize conda for the current shell session
    source "$HOME/miniconda/etc/profile.d/conda.sh"
    conda activate base
else
    echo "Conda is already installed."
fi

# 2. Install OpenJDK 21 via Conda Forge
echo "Installing OpenJDK from conda-forge..."
conda install -y -c conda-forge openjdk

# 3. Setup permissions and execute server script (simulated target)
chmod +x server.bat 2>/dev/null || chmod +x server.bat
./server.bat 2>/dev/null || ./server.sh
