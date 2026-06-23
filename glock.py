#!/usr/bin/env python3
import os
import subprocess
import sys

# --- CONFIGURATION ---
# Load token securely from environment. Set it in terminal using: export GITHUB_TOKEN="your_new_token"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_USER = "DefNotflexsman"
GITHUB_REPO = "server-att2"
BRANCH_NAME = "main"
# ---------------------


def run_cmd(command: list[str]) -> str:
    """Helper function to execute shell commands and handle errors securely."""
    # Safety fallback verification check
    if GITHUB_TOKEN and any(GITHUB_TOKEN in c for c in command):
        clean_cmd = " ".join(
            [c if GITHUB_TOKEN not in c else "[REDACTED_TOKEN]" for c in command]
        )
    else:
        clean_cmd = " ".join(command)

    print(f"Executing: {clean_cmd}")
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        error_msg = result.stderr.strip()
        if GITHUB_TOKEN and GITHUB_TOKEN in error_msg:
            error_msg = error_msg.replace(GITHUB_TOKEN, "[REDACTED]")
        print(f"Error occurred:\n{error_msg}\n", file=sys.stderr)
        return ""

    return result.stdout.strip()


def main() -> None:
    # Fixed the broken safety check logic condition
    if not GITHUB_TOKEN or GITHUB_TOKEN == "YOUR_PAT_TOKEN_HERE":
        print("Error: GITHUB_TOKEN environment variable is empty.")
        print("Please set it in your terminal first by running:")
        print('export GITHUB_TOKEN="your_actual_token_here"')
        sys.exit(1)

    # 1. Initialize Git if not already done
    if not os.path.exists(".git"):
        run_cmd(["git", "init"])
        run_cmd(["git", "config", "user.name", GITHUB_USER])
        run_cmd(
            ["git", "config", "user.email", f"{GITHUB_USER}@users.noreply.github.com"]
        )
    else:
        print("Git repository already initialized.")

    # 2. Stage all current directory files
    run_cmd(["git", "add", "."])

    # 3. Create a commit
    status = run_cmd(["git", "status", "--porcelain"])
    if not status:
        print("No changes or new files detected to commit.")
    else:
        run_cmd(
            ["git", "commit", "-m", "Automated backend sync from Jupyter environment"]
        )

    # 4. Set the branch name explicitly
    run_cmd(["git", "branch", "-M", BRANCH_NAME])

    # 5. Build authenticated URL and push code
    authenticated_url = (
        f"https://{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{GITHUB_REPO}.git"
    )

    print("\nPushing repository tracking to GitHub...")
    push_result = subprocess.run(
        ["git", "push", authenticated_url, BRANCH_NAME, "--force"],
        capture_output=True,
        text=True,
    )

    if push_result.returncode == 0:
        print("\n✅ Success! Your backend files have been pushed to GitHub.")
        print(f"Verify them at: https://github.com/{GITHUB_USER}/{GITHUB_REPO}")
    else:
        err = push_result.stderr.replace(GITHUB_TOKEN, "[REDACTED]")
        print(f"\n❌ Push failed. Details:\n{err}")


if __name__ == "__main__":
    main()
