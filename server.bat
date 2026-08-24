#!/bin/bash

URL="https://piston-data.mojang.com/v1/objects/8de3d0ea7adb85af0f87f764f3dc186cc87736a3/server.jar"

echo "Downloading Minecraft 1.21 Server JAR..."
curl -L -o server.jar "$URL"

echo "Pre-configuring EULA and Server Properties..."
echo "eula=true" > eula.txt
echo "online-mode=false" > server.properties

echo "Starting Minecraft 1.21 Server..."
java -Xmx2G -Xms2G -jar server.jar nogui
