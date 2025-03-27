import os
import requests
import time
from dotenv import load_dotenv
from colorama import Fore, Style, init
from datetime import datetime, timezone

# Initialize colorama for Windows CMD color support & ensure cross-platform compatibility
init(autoreset=True)

ENV_FILE = ".env"

def clear_terminal():
    """Clear the terminal screen based on the OS."""
    os.system('cls' if os.name == 'nt' else 'clear')

def setup_github_token():
    """Prompt the user for a GitHub token if not found, and guide them on how to get one."""
    if not os.path.exists(ENV_FILE):  # Only ask if .env doesn't exist
        print("\n🔹 Welcome to Repo Radar!")
        print("🚀 To get started, you need a **GitHub Personal Access Token**.")
        print("👉 Go to: https://github.com/settings/tokens/new to create one.")
        print("🔹 Enable **'repo' permissions** to track private repositories.")
        print("🔹 If GitHub updates the process, check their docs: https://docs.github.com/")
        print("🔹 Copy the token and paste it below.\n")

        token = input("🔑 Enter your GitHub token: ").strip()

        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write(f"GITHUB_TOKEN={token}\n")

        print("\n✅ Token saved! Restarting with authentication...\n")
        time.sleep(2)

# Ensure the token setup runs BEFORE fetching any repos
setup_github_token()
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("❌ Error: No GitHub token found. Restart and enter a valid token.")
    exit(1)

def get_authenticated_user():
    """Determine if the token belongs to an individual or an organization."""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get("https://api.github.com/user", headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        username = user_data.get("login")
        print(f"\n✅ Logged into GitHub as **{username}**.")
        return username
    else:
        print(f"❌ Authentication failed: {response.status_code}, {response.text}")
        exit(1)

def get_default_branch(repo):
    """Fetch the default branch of a repository."""
    url = f"https://api.github.com/repos/{repo}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("default_branch", "main")
    else:
        print(f"❌ Error fetching default branch: {response.status_code}, {response.text}")
        return "main"

def get_repos():
    """Fetch repositories based on the authentication type (personal account or organization)."""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    orgs_response = requests.get("https://api.github.com/user/orgs", headers=headers)

    if orgs_response.status_code == 200:
        orgs = orgs_response.json()
        if orgs:
            org_name = orgs[0]['login']
            repo_url = f"https://api.github.com/orgs/{org_name}/repos"
        else:
            repo_url = "https://api.github.com/user/repos"
    else:
        print(f"❌ Error fetching organization details: {orgs_response.status_code}, {orgs_response.text}")
        exit(1)

    response = requests.get(repo_url, headers=headers)
    if response.status_code == 200:
        repos = response.json()
        if not repos:
            print("\n🔹 No repositories found.")
            return []
        else:
            print("\n📡 Tracking the latest repositories:")
            repo_names = [repo['full_name'] for repo in repos[:10]]
            for repo in repo_names:
                print(f"  📂 {repo}")
            return repo_names
    else:
        print(f"❌ Error fetching repositories: {response.status_code}, {response.text}")
        return []

def get_pull_requests(repo, limit=5):
    """Fetch open pull requests for a given GitHub repository."""
    url = f"https://api.github.com/repos/{repo}/pulls"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        pulls = response.json()
        if not pulls:
            print(f"\n[PR] No open pull requests for {repo}.")
            return 0
        else:
            print(f"\n=== Open Pull Requests for {repo} (Latest {min(limit, len(pulls))}) ===\n")
            for pr in pulls[:limit]:
                pr_number = pr['number']
                print(f"  [PR #{pr_number}] {pr['title']}")
            return len(pulls)
    else:
        print(f"[ERROR] Failed to fetch PRs: {response.status_code}, {response.text}")
        return 0

def get_recent_commits(repo, limit=5):
    """Fetch recent commits with author, timestamp, and branch highlighting."""
    branch = get_default_branch(repo)
    url = f"https://api.github.com/repos/{repo}/commits?sha={branch}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        commits = response.json()
        if not commits:
            print(f"\n[COMMITS] No recent commits in {repo} on branch {branch}.")
            return 0
        else:
            print(f"\n=== Recent Commits for {repo} (Branch: {branch}) ===\n")
            for commit in commits[:limit]:
                commit_hash = commit['sha'][:7]
                commit_msg = commit['commit']['message'].split("\n")[0]
                commit_author = commit['commit']['author']['name']
                commit_date_str = commit['commit']['author']['date']

                commit_datetime = datetime.strptime(commit_date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                commit_utc_time = commit_datetime.strftime("%H:%M:%S (UTC)")

                today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                commit_date_display = "Today" if commit_datetime.strftime("%Y-%m-%d") == today_str else commit_datetime.strftime("%Y-%m-%d")

                color = Fore.RED if branch == "main" else Fore.WHITE

                print(color + f"  [{commit_hash}] {commit_msg}")
                print(f"     Author: {commit_author} | Date: {commit_date_display}, {commit_utc_time}" + Style.RESET_ALL)
            return len(commits)
    else:
        print(f"[ERROR] Failed to fetch commits: {response.status_code}, {response.text}")
        return 0

def track_repos(refresh_interval=60):
    """Continuously track PRs & commits for all repos."""
    while True:
        clear_terminal()
        print("\n📡 **Repo Radar** - Live GitHub Tracking\n")
        
        repo_list = get_repos()

        if not repo_list:
            print("❌ No repositories found. Exiting...")
            break

        for repo in repo_list:
            get_pull_requests(repo)
            get_recent_commits(repo)

        print(f"\n🔄 Next update in {refresh_interval} seconds...\n")
        time.sleep(refresh_interval)

# Authenticate user and auto-detect repos
get_authenticated_user()
track_repos(refresh_interval=60)
