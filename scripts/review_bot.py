import os
from github import Github
from openai import OpenAI

# Environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")
pr_number = int(os.getenv("PR_NUMBER"))
repo_name = os.getenv("REPO_NAME")

# Set up clients
client = OpenAI(api_key=openai_api_key)
g = Github(github_token)
repo = g.get_repo(repo_name)
pr = repo.get_pull(pr_number)

print(f"🔍 Reviewing PR #{pr_number} - {pr.title}")

# Get PR diff
diffs = pr.diff_url
files = pr.get_files()
diff_summary = ""
for file in files:
    diff_summary += f"\n--- {file.filename} ---\n{file.patch if file.patch else ''}"

print("💬 Sending diff to GPT-4...")

# GPT review
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "system",
            "content": "You are a senior software engineer reviewing a GitHub pull request.",
        },
        {
            "role": "user",
            "content": f"Please review this PR diff:\n{diff_summary}\n\nReturn issues if any, otherwise respond with 'LGTM'.",
        },
    ],
)

review = response.choices[0].message.content
print("🧠 GPT Review:\n", review)

# Post comment
pr.create_issue_comment(f"🤖 **AI Review**:\n{review}")

# Auto-approve & merge if LGTM
if "lgtm" in review.lower():
    pr.create_review(event="APPROVE")
    pr.merge(commit_message="✅ Auto-merged by SmartMerge bot (GPT-approved)")
    print("✅ PR auto-approved and merged.")
else:
    print("🛑 PR requires manual review.")
