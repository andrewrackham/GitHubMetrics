import argparse
import json
from datetime import datetime, time
from pathlib import Path

import yaml
from business_duration import businessDuration


def compute_business_hours(start, end):
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--teams", required=True)
    args = parser.parse_args()

    with open(args.input) as f:
        raw_data = json.load(f)

    teams = load_teams(args.teams)
    team_lookup = {
        member: team for team, members in teams.items() for member in members
    }

    metrics = []
    for pr in raw_data:
        created = datetime.fromisoformat(pr["created_at"])
        merged = datetime.fromisoformat(pr["merged_at"]) if pr.get("merged_at") else None
        ready = datetime.fromisoformat(pr["ready_for_review_at"]) if pr.get("ready_for_review_at") else None
        comment_time = datetime.fromisoformat(pr["first_comment_at"]) if pr.get("first_comment_at") else None
        approval = datetime.fromisoformat(pr["second_approval_at"]) if pr.get("second_approval_at") else None

        metrics.append({
            "author": pr["author"],
            "team": team_lookup.get(pr["author"], "unknown"),
            "created_at": pr["created_at"],
            "ready_for_review_at": pr.get("ready_for_review_at"),
            "first_comment_at": pr.get("first_comment_at"),
            "approved_at": pr.get("second_approval_at"),
            "merged_at": pr.get("merged_at"),

            "time_to_first_comment_hrs": compute_business_hours(created, comment_time),
            "time_to_first_approval_hrs": compute_business_hours(created, approval),
            "time_to_merge_hrs": compute_business_hours(created, merged),

            "lines_added": pr.get("additions", 0),
            "lines_deleted": pr.get("deletions", 0),
            "files_changed": pr.get("changed_files", 0),
            "comment_count": pr.get("comment_count", 0)
        })

    Path("data").mkdir(exist_ok=True)
    with open("data/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("Metrics written to data/metrics.json")


if __name__ == "__main__":
    main()
