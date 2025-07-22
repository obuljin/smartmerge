import os
import openai
from github import Github

# Get environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")
pr_number = int(os.getenv("PR_NUMBER"))
repo_name = os.getenv("REPO_NAME")

# Authenticate with GitHub
gh = Github(github_token)
repo = gh.get_repo(repo_name)
pr = repo.get_pull(pr_number)

print(f"🔍 Reviewing PR #{pr_number} - {pr.title}")

# Get code diffs
diffs = ""
for file in pr.get_files():
    if file.patch:
        diffs += f"\nFile: {file.filename}\n{file.patch}\n"

if not diffs:
    print("No diff found.")
    exit(0)

# Send diff to OpenAI
print("💬 Sending diff to GPT-4...")
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a senior software engineer reviewing a GitHub pull request."},
        {"role": "user", "content": f"Please review this PR diff:\n{diffs}\n\nReturn any issues or say 'LGTM' if clean."}
    ]
)

review = response['choices'][0]['message']['content']
print("✅ GPT-4 Review:\n", review)

# Post comment to PR
pr.create_issue_comment(f"🤖 **AI Review**:\n\n{review}")

# Auto-approve and merge if LGTM
if "lgtm" in review.lower() or "looks good" in review.lower():
    print("✅ Looks good. Approving and merging...")
    pr.create_review(event="APPROVE")
    pr.merge(merge_method="merge")
else:
    print("❌ Issues found, not merging.")
