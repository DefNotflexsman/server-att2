#!/usr/bin/env bash
set -e

# Set working directories
SERVER_DIR="$(pwd)"
JAVA_DIR="${SERVER_DIR}/local_jdk_21"
DATA_DIR="${SERVER_DIR}/data"

mkdir -p "$DATA_DIR"

# 1. Download and Extract Portable OpenJDK 21 if missing
if [ ! -d "$JAVA_DIR" ]; then
    echo "Portable Java not found. Downloading OpenJDK 21..."
    JAVA_TAR_URL="https://api.adoptium.net/v3/binary/latest/21/ga/linux/x64/jdk/hotspot/normal/eclipse"
    
    curl -sL -A "Mozilla/5.0" "$JAVA_TAR_URL" -o openjdk21.tar.gz
    
    echo "Extracting OpenJDK 21..."
    mkdir -p "$JAVA_DIR"
    tar -xzf openjdk21.tar.gz -C "$JAVA_DIR" --strip-components=1
    rm openjdk21.tar.gz
    echo "Java installation ready!"
fi

JAVA_BIN="${JAVA_DIR}/bin/java"
chmod +x "$JAVA_BIN"

# 2. Download Paper 1.21.1 Server JAR
cd "$DATA_DIR"
PAPER_JAR="paper-1.21.1.jar"

if [ ! -f "$PAPER_JAR" ]; then
    echo "Downloading Paper 1.21.1..."
    curl -sH "User-Agent: Mozilla/5.0" -o "$PAPER_JAR" \
    "https://papermc.io/v1/paper/1.17.1/latest/download"
fi

# 3. Configure Server Configuration
echo "eula=true" > eula.txt

if [ ! -f "server.properties" ]; then
    cat <<EOF > server.properties
online-mode=${ONLINE_MODE:-false}
server-port=25565
max-players=5
view-distance=6
simulation-distance=4
network-compression-threshold=64
EOF
fi

# 4. Launch Server using the Portable Java Binary
echo "Starting Minecraft Server..."
exec "$JAVA_BIN" -Xms512M -Xmx${MAX_RAM:-1024M} \
  -XX:+UseG1GC \
  -XX:+ParallelRefProcEnabled \
  -XX:MaxGCPauseMillis=200 \
  -XX:+UnlockExperimentalVMOptions \
  -XX:+DisableExplicitGC \
  -XX:+AlwaysPreTouch \
  -XX:G1NewSizePercent=30 \
  -XX:G1MaxNewSizePercent=40 \
  -XX:G1HeapRegionSize=8M \
  -XX:G1ReservePercent=20 \
  -XX:G1HeapWastePercent=5 \
  -XX:G1MixedGCCountTarget=4 \
  -XX:InitiatingHeapOccupancyPercent=15 \
  -XX:G1MixedGCLiveThresholdPercent=90 \
  -XX:G1RSetUpdatingPauseTimePercent=5 \
  -XX:SurvRatio=8 \
  -XX:+UseStringDeduplication \
  -jar "$PAPER_JAR" --nogui