from __future__ import annotations

import base64
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

GITHUB_API_BASE = "https://api.github.com"

@dataclass
class GitHubRepo:
    name: str
    full_name: str
    private: bool
    html_url: str
    clone_url: str
    ssh_url: str
    archived: bool

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "GitHubRepo":
        return cls(
            name=data.get("name", ""),
            full_name=data.get("full_name", ""),
            private=bool(data.get("private", False)),
            html_url=data.get("html_url", ""),
            clone_url=data.get("clone_url", ""),
            ssh_url=data.get("ssh_url", ""),
            archived=bool(data.get("archived", False)),
        )

class GitHubClient:
    def __init__(self, token: str, api_base: str = GITHUB_API_BASE) -> None:
        if not token:
            raise ValueError("GitHub personal access token must not be empty.")
        self.token = token.strip()
        self.api_base = api_base.rstrip("/")

    def _build_request(
        self,
        path: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[bytes] = None,
    ) -> Request:
        url = f"{self.api_base}/{path.lstrip('/')}"
        if params:
            query = urlencode(params)
            url = f"{url}?{query}"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "Personal-GitHub-Repo-Grabber",
        }
        if data:
            headers["Content-Type"] = "application/json"

        return Request(url=url, headers=headers, method=method, data=data)

    def _send_request(self, request: Request) -> Any:
        try:
            with urlopen(request, timeout=15) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                raw = response.read().decode(charset)
                return json.loads(raw) if raw else None
        except HTTPError as exc:
            # Read detailed error message from GitHub if available
            err_body = exc.read().decode("utf-8") if exc else ""
            raise RuntimeError(f"GitHub API Error {exc.code}: {exc.reason} - {err_body}") from exc
        except URLError as exc:
            raise RuntimeError(f"Network error: {exc}") from exc

    def list_authenticated_user_repos(self) -> List[GitHubRepo]:
        repos: List[GitHubRepo] = []
        request = self._build_request("user/repos", params={"per_page": 100})
        data = self._send_request(request)
        if isinstance(data, list):
            for item in data:
                repos.append(GitHubRepo.from_api(item))
        return repos

    def upload_file_to_repo(self, owner: str, repo: str, file_path: str, file_content: bytes) -> None:
        """Uploads or updates a file directly via the GitHub Contents API."""
        path = f"repos/{owner}/{repo}/contents/{file_path}"
        
        # GitHub requires files uploaded via API to be Base64 encoded strings
        encoded_content = base64.b64encode(file_content).decode("utf-8")
        
        # First, check if the file already exists to get its 'sha' fingerprint (required for updates)
        sha = None
        try:
            check_req = self._build_request(path, method="GET")
            existing_data = self._send_request(check_req)
            if isinstance(existing_data, dict) and "sha" in existing_data:
                sha = existing_data["sha"]
        except Exception:
            # File doesn't exist yet, which is fine
            pass

        # Build the upload instructions payload
        payload = {
            "message": f"Upload {file_path} via Python Web Script",
            "content": encoded_content
        }
        if sha:
            payload["sha"] = sha

        json_bytes = json.dumps(payload).encode("utf-8")
        upload_req = self._build_request(path, method="PUT", data=json_bytes)
        self._send_request(upload_req)


def load_token_from_env() -> str:
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if not token:
        raise RuntimeError("GitHub token not found. Please set the 'GITHUB_TOKEN' environment variable.")
    return token


def main() -> int:
    try:
        token = load_token_from_env()
        client = GitHubClient(token=token)

        # 1. Ask the interactive query
        user_response = input("Do you want to update a repo? [yes,no]: ").strip().lower()

        if user_response == "yes":
            # 2. Parse target layout format: username/repo-name
            target = input("Enter target repository as <username>/<repo-name>: ").strip()
            if "/" not in target:
                print("Error: Format must be exactly 'username/repo-name'")
                return 1
                
            owner, repo_name = target.split("/", 1)

            # 3. Read all files in the current workspace directory (the 'ls' logic)
            current_directory = os.getcwd()
            print(f"\nScanning workspace files in: {current_directory}")
            
            files_to_upload = []
            for item in os.listdir(current_directory):
                item_path = os.path.join(current_directory, item)
                # Only grab files, skip sub-directories to prevent infinite loops
                if os.path.isfile(item_path):
                    files_to_upload.append(item)

            if not files_to_upload:
                print("No files found in the current directory to upload.")
                return 0

            print(f"Found {len(files_to_upload)} files to push: {files_to_upload}\n")
            
            # 4. Push every file sequentially over the network
            for file_name in files_to_upload:
                print(f"Uploading: {file_name} ...")
                try:
                    with open(file_name, "rb") as f:
                        binary_data = f.read()
                    
                    client.upload_file_to_repo(
                        owner=owner,
                        repo=repo_name,
                        file_path=file_name,
                        file_content=binary_data
                    )
                    print(f"✅ Successfully pushed {file_name}")
                except Exception as file_err:
                    print(f"❌ Failed to upload {file_name}: {file_err}")

            print("\nAll operations finalized.")
        else:
            print("Exiting program.")
            sys.exit(0)

        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())