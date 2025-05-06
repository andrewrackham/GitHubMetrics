import argparse
import json
from datetime import datetime

from py_markdown_table.markdown_table import markdown_table

WORKING_HOURS = 8


def main(input_file, output_file):
    metrics = load_metrics(input_file)

    pull_request_table = build_pull_request_table(metrics)
    with open(output_file, 'w') as f:
        f.write("# GitHub PR Metrics Report\n\n")

        f.write("## Monthly Stats\n")
        f.write(pull_request_table + "\n")

        # f.write("## Overall Stats\n")
        # for key, value in metrics['overall'].items():
        #     f.write(f"- **{key}**: {value}\n")
        #
        # f.write("\n## Per User Stats\n")
        # for user, data in metrics['by_user'].items():
        #     f.write(f"### {user}\n")
        #     for k, v in data.items():
        #         f.write(f"- {k}: {v}\n")
        #
        # f.write("\n## Per Team Stats\n")
        # for team, data in metrics['by_team'].items():
        #     f.write(f"### {team}\n")
        #     for k, v in data.items():
        #         f.write(f"- {k}: {v}\n")


def build_pull_request_table(metrics):
    data = []
    for pull_request in metrics["pull_requests"]:
        if pull_request["approved_at"] is None:
            continue

        data.append({
            "PR": pull_request["number"],
            "Created": pull_request["created_at"],

            "First Commit": to_readable_time(pull_request["first_commit_at"]),
            "Last Commit": to_readable_time(pull_request["last_commit_at"]),
            "Ready for Review": to_readable_time(pull_request["ready_for_review_at"]),
            "First Feedback": to_readable_time(pull_request["first_feedback_at"]),
            "Approved": to_readable_time(pull_request["approved_at"]),
            "Merged": to_readable_time(pull_request["merged_at"]),

            "First Commit To Production (Hrs)": format_duration(pull_request["first_commit_to_production"]),
            "Code Complete To Production (Hrs)": format_duration(pull_request["code_complete_to_production"]),
            "Feedback Delay (Hrs)": format_duration(pull_request["feedback_delay"]),
            "Code Review Duration (Hrs)": format_duration(pull_request["code_review_duration"]),
            # "Code Review Duration (Hrs)": format_duration(pull_request["code_review_duration_with_feedback"]),
            "Time in Active Development (Hrs)": format_duration(pull_request["active_development_duration"]),
        })

    return markdown_table(data).set_params(row_sep='markdown',
                                           quote=False).get_markdown()


def to_readable_time(value: str):
    return datetime.fromisoformat(value).strftime('%d/%m/%Y %I:%M%p')


def format_duration(value: float):
    whole_days = int(value / WORKING_HOURS)
    whole_hours = int(value % WORKING_HOURS)
    whole_minutes = round((value - whole_hours) * 60)

    elements = []
    if whole_days > 0:
        elements.append(f"{whole_days}d")
    if whole_hours > 0:
        elements.append(f"{whole_hours}h")
    if whole_minutes > 0:
        elements.append(f"{whole_hours}m")

    return ' '.join(elements)


def load_metrics(input_file):
    with open(input_file) as file_stream:
        metrics = json.load(file_stream)
    return metrics


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    main(args.input, args.output)
