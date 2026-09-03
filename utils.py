# utils.py
import shutil
import asyncio

async def ensure_java_installed():
    """Checks if Java exists in system PATH, attempts installation if missing."""
    if shutil.which("java") is not None:
        return True

    print("Java binary missing. Attempting runtime installation...")
    try:
        # Check package manager and install openjdk
        proc = await asyncio.create_subprocess_exec(
            "sudo", "apt-get", "update", "&&", "sudo", "apt-get", "install", "-y", "default-jre",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        return shutil.which("java") is not None
    except Exception as e:
        print(f"Failed to install Java: {e}")
        return False