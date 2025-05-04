import argparse
import json
from datetime import datetime, time
from pathlib import Path

import yaml
from business_duration import businessDuration

REQUIRED_APPROVALS = 2


def business_hours_delta(start, end):
    if not start or not end:
        return None
    return round(
        businessDuration(
            start,
            end,
            starttime=time(9, 0),
            endtime=time(17, 0),
            weekendlist=[6, 7],  # Saturday & Sunday
            holidaylist=[]
        ), 2
    )


def load_teams(path):
    with open(path) as f:
        return yaml.safe_load(f)


def main(pull_requests, teams):
    team_lookup = {
        member: team for team, members in teams.items() for member in members
    }

    metrics = []
    for pr in pull_requests:
        team = team_lookup.get(pr["author"], "unknown")
        metrics.append(build_metric(pr, team))

    save_metrics(metrics)


def save_metrics(metrics):
    Path("data").mkdir(exist_ok=True)
    with open("data/metrics.json", "w") as file_stream:
        json.dump(metrics, file_stream, indent=2)

    print("Metrics written to data/metrics.json")


def time_of_approval(reviews):
    approved_at = None
    approved_by = []
    changes_requested_by = []

    for review in reviews:
        user = review["user"]
        state = review["state"]
        if state == "APPROVED":
            if user not in approved_by: approved_by.append(user)
            if user in changes_requested_by: changes_requested_by.remove(user)
        if state == "DISMISSED":
            if user in approved_by: approved_by.remove(user)
            if user in changes_requested_by: changes_requested_by.remove(user)
        if state == "CHANGES_REQUESTED":
            if user in approved_by: approved_by.remove(user)
            if user not in changes_requested_by: changes_requested_by.append(user)

        if len(approved_by) == REQUIRED_APPROVALS:
            approved_at = review["submitted_at"]

    if (len(approved_by) >= REQUIRED_APPROVALS) and (len(changes_requested_by) == 0):
        return datetime.fromisoformat(approved_at)

    return None


def build_metric(pull_request, team):
    """
    What we're looking to show:
        - decreasing time to production
            - Need: time between first commit and merge
        - decreasing time for completed work to reach production
            - Need time between last commit and merge
        - decreasing feedback time
            - Need: time between ready for review and first review
        - decreasing time in code review
            - Need: time between ready for review and approval
        - decreasing duration of active development
            - Need: time between first commit and last commit
        - understand of engagement on PRs
            - Need: total number of comments on PR
    """

    first_commit_at = time_of_first_commit(pull_request)
    last_commit_at = time_of_last_commit(pull_request)
    merged_at = time_of_merge(pull_request)
    ready_for_review_at = time_when_ready_for_review(pull_request)
    first_feedback_at = time_of_first_feedback(pull_request)
    approved_at = time_of_approval(pull_request["reviews"])

    return {
        "number": pull_request["number"],
        "author": pull_request["author"],
        "team": team,

        "first_commit_at": first_commit_at.isoformat() if first_feedback_at else None,
        "last_commit_at": last_commit_at.isoformat() if last_commit_at else None,
        "merged_at": merged_at.isoformat() if merged_at else None,
        "ready_for_review_at": ready_for_review_at.isoformat() if ready_for_review_at else None,
        "first_feedback_at": first_feedback_at.isoformat() if first_feedback_at else None,
        "approved_at": approved_at.isoformat() if approved_at else None,

        "first_commit_to_production": business_hours_delta(first_commit_at, merged_at),
        "code_complete_to_production": business_hours_delta(last_commit_at, merged_at),
        "feedback_delay": business_hours_delta(ready_for_review_at, first_feedback_at),
        "code_review_duration": business_hours_delta(ready_for_review_at, approved_at),
        "active_development_duration": business_hours_delta(first_commit_at, last_commit_at),

        "lines_added": pull_request.get("additions", 0),
        "lines_deleted": pull_request.get("deletions", 0),
        "files_changed": pull_request.get("changed_files", 0),
        "comment_count": pull_request.get("comments", 0)
    }


def time_when_ready_for_review(pull_request):
    return datetime.fromisoformat(
        pull_request.get("ready_for_review_at") if pull_request.get("ready_for_review_at") else pull_request.get(
            "created_at"))


def time_of_first_feedback(pull_request):
    reviews = pull_request.get("reviews")
    return datetime.fromisoformat(reviews[0].get("submitted_at")) if len(reviews) > 0 else None


def time_of_merge(pull_request):
    return datetime.fromisoformat(pull_request.get("merged_at")) if pull_request.get("merged_at") else None


def time_of_last_commit(pull_request):
    commits = pull_request.get("commits")
    return datetime.fromisoformat(commits[-1].get("timestamp")) if len(commits) > 0 else None


def time_of_first_commit(pull_request):
    commits = pull_request.get("commits")
    return datetime.fromisoformat(commits[0].get("timestamp")) if len(commits) > 0 else None


def load_pr_data(file_url: str):
    with open(file_url) as f:
        raw_data = json.load(f)
    return raw_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--teams", required=True)
    args = parser.parse_args()

    main(load_pr_data(args.input), load_teams(args.teams))
