#!/usr/bin/env bash
set -e

# Create server directory if it doesn't exist
mkdir -p /data
cd /data

PAPER_JAR="paper-1.21.1.jar"

# Download Paper 1.21.1 (Build 119 as an example stable release) if not present
if [ ! -f "$PAPER_JAR" ]; then
    echo "Downloading Paper 1.21.1..."
    curl -sH "User-Agent: Mozilla/5.0" -o "$PAPER_JAR" \
    "https://api.papermc.io/v2/projects/paper/versions/1.21.1/builds/119/downloads/paper-1.21.1-119.jar"
fi

# Auto-accept EULA via environment variable or default
if [ "${EULA,,}" = "true" ]; then
    echo "eula=true" > eula.txt
fi

# Write minimal server.properties if absent
if [ ! -f "server.properties" ]; then
    cat <<EOF > server.properties
online-mode=${ONLINE_MODE:-true}
server-port=25565
max-players=5
view-distance=6
simulation-distance=4
network-compression-threshold=64
EOF
fi

# Aikar's JVM Flags optimized for 1GB - 2GB RAM limits
exec java -Xms512M -Xmx${MAX_RAM:-1024M} \
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