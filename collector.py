import argparse
import json
import os
from datetime import datetime, timezone, date
from pathlib import Path

from github import Github
from github.PaginatedList import PaginatedList
from github.PullRequest import PullRequest

READY_FOR_REVIEW = "ready_for_review"
UNKNOWN_USER = "unknown"
NO_TIME = ''
NO_LABEL = ''


def extract_events(pr: PullRequest) -> list[dict]:
    events = []
    for event in pr.get_issue_events():
        events.append({
            "actor": event.actor.login if event.actor else UNKNOWN_USER,
            "action": event.event,
            "timestamp": event.created_at.isoformat(),
            "label": event.label.name if event.label else NO_LABEL
        })
    return events


def extract_commits(pr: PullRequest) -> list[dict]:
    commits = []
    for commit in pr.get_commits():
        commits.append({
            "author": commit.author.login if commit.author else UNKNOWN_USER,
            "timestamp": commit.commit.author.date.isoformat()
        })
    return commits


def extract_reviews(pr: PullRequest) -> list[dict]:
    reviews = []
    for review in pr.get_reviews():
        reviews.append({
            "user": review.user.login,
            "submitted_at": review.submitted_at.isoformat(),
            "state": review.state,
        })
    return reviews


def main(repo_name: str, start: date, end: date):
    gh = Github(os.getenv('GITHUB_TOKEN'))
    repo = gh.get_repo(repo_name)

    print(f"Fetching pull requests for {repo_name}...")
    pulls = repo.get_pulls(state='all', sort='created', direction='desc')

    data = filter_pull_request_data(pulls, end, start)
    print(f"Total {len(data)} PRs fetched")

    Path("data").mkdir(exist_ok=True)
    with open('data/raw.json', 'w') as file_stream:
        json.dump(data, file_stream, indent=2)

    print("Raw Data written to data/raw.json")


def filter_pull_request_data(pulls: PaginatedList[PullRequest], end: date, start: date) -> list[dict]:
    data = []
    for pr in pulls:
        if pr.created_at > end:
            continue

        if pr.created_at < start or pr.created_at > end:
            print(f"Exiting at PR #{pr.number} (created at {pr.created_at})")
            break

        print(f"Processing PR #{pr.number} (created at {pr.created_at})")
        pull_request_data = build_pull_request_data(pr)

        data.append(pull_request_data)
    return data


def build_pull_request_data(pr: PullRequest) -> dict[str, any]:
    pull_request_data = {
        "number": pr.number,
        "title": pr.title,
        "author": pr.user.login,
        "created_at": pr.created_at.isoformat(),
        "merged_at": pr.merged_at.isoformat() if pr.merged_at else NO_TIME,
        "closed_at": pr.closed_at.isoformat() if pr.closed_at else NO_TIME,
        "state": pr.state,
        "assignees": [assignee.login for assignee in pr.assignees],
        "labels": [label.name for label in pr.labels],
        "draft": pr.draft,
        "additions": pr.additions,
        "deletions": pr.deletions,
        "changed_files": pr.changed_files,
        "comments": pr.comments,
        "reviews": extract_reviews(pr),
        "events": extract_events(pr),
        "commits": extract_commits(pr),
    }
    return pull_request_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', required=True)
    parser.add_argument('--start', required=True)
    parser.add_argument('--end', required=True)
    args = parser.parse_args()

    main(
        args.repo,
        datetime.fromisoformat(args.start).replace(tzinfo=timezone.utc),
        datetime.fromisoformat(args.end).replace(tzinfo=timezone.utc)
    )
