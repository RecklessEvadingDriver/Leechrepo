#!/bin/bash
# Heroku post-compile hook to install aria2

echo "-----> Installing aria2..."

# Create a temporary directory
mkdir -p /tmp/aria2-install
cd /tmp/aria2-install

# Download and install aria2
ARIA2_VERSION="1.37.0"
wget -q "https://github.com/aria2/aria2/releases/download/release-${ARIA2_VERSION}/aria2-${ARIA2_VERSION}.tar.gz"

if [ $? -eq 0 ]; then
    tar -xzf "aria2-${ARIA2_VERSION}.tar.gz"
    cd "aria2-${ARIA2_VERSION}"
    
    ./configure --prefix=$HOME/.heroku/aria2 --without-libxml2 --without-libexpat --without-sqlite3
    make -j4
    make install
    
    # Add to PATH
    export PATH="$HOME/.heroku/aria2/bin:$PATH"
    
    echo "-----> aria2 installation complete"
else
    echo "-----> aria2 download failed, will use system aria2 if available"
fi

# Clean up
cd /
rm -rf /tmp/aria2-install
