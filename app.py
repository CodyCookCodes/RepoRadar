import os
import requests
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
ENV_FILE = ".env"

# Load environment variables if .env exists
if os.path.exists(ENV_FILE):
    load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def save_github_token(token):
    """Save the GitHub token to .env and reload it."""
    with open(ENV_FILE, "w") as f:
        f.write(f"GITHUB_TOKEN={token}\n")
    global GITHUB_TOKEN
    GITHUB_TOKEN = token


def get_authenticated_user():
    """Get the authenticated GitHub username."""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get("https://api.github.com/user", headers=headers)

    if response.status_code == 200:
        return response.json().get("login", "Unknown User")
    return None


def get_branches(repo):
    """Fetch all branches for a given repository."""
    url = f"https://api.github.com/repos/{repo}/branches"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        branches = [branch['name'] for branch in response.json()]
        return branches if branches else ["No branches found"]
    return []


def get_pull_requests(repo):
    """Get open pull requests."""
    url = f"https://api.github.com/repos/{repo}/pulls"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        prs = response.json()
        return [
            {"number": pr['number'], "title": f"🔔 {pr['title']}", "url": pr['html_url']}
            for pr in prs
        ] if prs else []
    return []


def get_commits_for_branch(repo, branch):
    """Fetch commits for a given branch."""
    url = f"https://api.github.com/repos/{repo}/commits?sha={branch}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    return []


def fetch_commits(repo, branches):
    """Fetch commits from all branches."""
    commits = {"main": [], "all": []}
    main_commits_hashes = []

    for branch in branches:
        commits_for_branch = get_commits_for_branch(repo, branch)

        for commit in commits_for_branch[:5]:  # Limit to 5 most recent commits per branch
            commit_hash = commit['sha'][:7]
            commit_msg = commit['commit']['message'].split("\n")[0]
            commit_author = commit['commit']['author']['name']
            commit_date_str = commit['commit']['author']['date']

            commit_datetime = datetime.strptime(commit_date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            commit_utc_time = commit_datetime.strftime("%H:%M:%S (UTC)")

            current_time = datetime.now(timezone.utc)

            if commit_datetime.date() == current_time.date():
                commit_date_display = "Today"
            elif commit_datetime.date() == (current_time - timedelta(days=1)).date():
                commit_date_display = "Yesterday"
            else:
                commit_date_display = commit_datetime.strftime("%Y-%m-%d")

            commit_entry = {
                "hash": commit_hash,
                "message": commit_msg,
                "author": commit_author,
                "date": f"{commit_date_display}, {commit_utc_time}",
                "branch": branch
            }

            if branch == "main":
                commits["main"].append(commit_entry)
                main_commits_hashes.append(commit_hash)
            else:
                commit_entry["is_main"] = commit_hash in main_commits_hashes
                commits["all"].append(commit_entry)

    return commits


@app.route("/", methods=["GET", "POST"])
def setup():
    """Show the setup page if no GitHub token is found."""
    if not GITHUB_TOKEN:
        if request.method == "POST":
            github_token = request.form.get("github_token").strip()
            if github_token:
                save_github_token(github_token)
                return redirect(url_for("home"))
        return render_template("setup.html")

    return redirect(url_for("home"))


@app.route("/dashboard", methods=["GET", "POST"])
def home():
    """Main dashboard showing PRs and commits."""
    user = get_authenticated_user()
    repo_data = []

    repo_filter = request.args.getlist("repo_filter")
    repos = get_repos()

    # Filter repos based on user selection
    if repo_filter:
        repos = [repo for repo in repos if repo in repo_filter]

    for repo in repos[:6]:  # Limit to 6 repos for now
        prs = get_pull_requests(repo)
        branches = get_branches(repo)
        commits = fetch_commits(repo, branches)

        repo_data.append({
            "name": repo,
            "prs": prs,
            "commits_main": commits["main"],
            "commits_all": commits["all"]
        })

    return render_template("dashboard.html", user=user, repo_data=repo_data, repos=repos)


def get_repos():
    """Get repositories from both organizations and personal GitHub account."""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Get organizations the user belongs to
    orgs_response = requests.get("https://api.github.com/user/orgs", headers=headers)
    
    repos = []
    
    if orgs_response.status_code == 200 and orgs_response.json():
        # Only get org repos if the user belongs to any organizations
        orgs = orgs_response.json()
        for org in orgs:
            org_name = org['login']
            repo_url = f"https://api.github.com/orgs/{org_name}/repos"
            org_repos_response = requests.get(repo_url, headers=headers)
            if org_repos_response.status_code == 200:
                repos.extend([repo['full_name'] for repo in org_repos_response.json()])
    
    # Fetch personal repositories if user is not part of any organizations or in addition to organizations
    personal_repos_response = requests.get("https://api.github.com/user/repos", headers=headers)
    if personal_repos_response.status_code == 200:
        repos.extend([repo['full_name'] for repo in personal_repos_response.json()])
    
    return repos



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
