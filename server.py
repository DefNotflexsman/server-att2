import os
import subprocess
import urllib.request
import sys

# 1. Configuration
REPO_URL = "https://github.com/ngrok/python-sdk-example.git"  # Switched to HTTPS for seamless Jupyter downloads
DIR_NAME = "python-sdk-example"
AUTHTOKEN = "3DXMqQlAz6xsVt4hFUjNuP6jkZ3_49rnPZD6ejBSrjcPmfM4P"

# 2. Clone the repository if it doesn't exist
if not os.path.exists(DIR_NAME):
    print(f"Cloning {REPO_URL}...")
    subprocess.run(["git", "clone", REPO_URL], check=True)
else:
    print(f"Directory '{DIR_NAME}' already exists. Skipping clone.")

# 3. Change directory context
os.chdir(DIR_NAME)

# 4. Install dependencies inside the environment
print("Installing requirements.txt...")
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

# 5. Set the environment variable and run the application
print("Starting the Ngrok Python SDK script...")
env = os.environ.copy()
env["NGROK_AUTHTOKEN"] = AUTHTOKEN

# Execute main.py and keep it interactive in your terminal
subprocess.run([sys.executable, "main.py"], env=env, check=True)

# 1. Define Server configurations
JAR_URL = "https://piston-data.mojang.com/v1/objects/8de3d0ea7adb85af0f87f764f3dc186cc87736a3/server.jar"
JAR_NAME = "server.jar"

# 2. Download the Minecraft Server JAR if it doesn't already exist
if not os.path.exists(JAR_NAME):
    print("Downloading Minecraft 1.21 Server JAR...")
    # Using a browser User-Agent string to bypass strict cloud firewalls
    req = urllib.request.Request(
        JAR_URL, 
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req) as response, open(JAR_NAME, 'wb') as out_file:
        out_file.write(response.read())
    print("Download complete!")
else:
    print("Server JAR already exists. Skipping download.")

# 3. Pre-configure EULA and Cracked Server Properties
print("Pre-configuring EULA and Server Properties...")
with open("eula.txt", "w", encoding="utf-8") as eula_file:
    eula_file.write("eula=true\n")

with open("server.properties", "w", encoding="utf-8") as props_file:
    props_file.write("online-mode=false\n")

# 4. Start the Minecraft Server runtime process
print("Starting Minecraft 1.21 Server...")
java_command = ["java", "-Xmx2G", "-Xms2G", "-jar", JAR_NAME, "nogui"]

# Execute the Java process and pipe input/output cleanly to the console
subprocess.run(java_command, check=True)
