import argparse
import json
from datetime import datetime

from py_markdown_table.markdown_table import markdown_table

WORKING_HOURS = 8


def main(input_file: str, output_file: str, team: str):
    metrics = load_metrics(input_file)

    monthly_table = build_monthly_table(metrics["teams"][team]["per_month"])
    weekly_table = build_weekly_table(metrics["teams"][team]["per_week"])
    pull_request_table = build_pull_request_table(metrics["pull_requests"])
    with open(output_file, 'w') as file_stream:
        file_stream.write(f"# {team} PR Metrics Report\n\n")

        file_stream.write("## Monthly Stats\n")
        file_stream.write(monthly_table + "\n")

        file_stream.write("## Weekly Stats\n")
        file_stream.write(weekly_table + "\n")

        file_stream.write("## Pull Requests\n")
        file_stream.write(pull_request_table + "\n")

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


def build_monthly_table(metrics):
    return build_duration_row("Month", metrics)


def build_weekly_table(metrics):
    return build_duration_row("Week", metrics)


def build_duration_row(label, metrics):
    data = list[dict[str, any]]()
    for key, source in metrics.items():
        totals = source["totals"]
        averages = source["averages"]

        row = {
            label: key,
            "Count": source["count"],

            "Avg First Commit To Production (Hrs)": format_duration(averages["first_commit_to_production"]),
            "Avg Code Complete To Production (Hrs)": format_duration(averages["code_complete_to_production"]),
            "Avg Feedback Delay (Hrs)": format_duration(averages["feedback_delay"]),
            "Avg Code Review Duration (Hrs)": format_duration(averages["code_review_duration"]),
            "Avg Time in Active Development (Hrs)": format_duration(averages["active_development_duration"]),

            "Avg Lines Added": averages["lines_added"],
            "Avg Lines Deleted": averages["lines_deleted"],
            "Avg Files Changed": averages["files_changed"],
            "Avg Comment Count": averages["comment_count"],
            "Total Comment Count": totals["comment_count"],
        }

        data.append(row)
    return markdown_table(data).set_params(row_sep='markdown',
                                           quote=False).get_markdown()


def build_pull_request_table(metrics):
    data = list[dict[str, any]]()
    for row_source in metrics:
        if row_source["approved_at"] is None:
            continue

        row = {
            "PR": row_source["number"],
        }
        format_metrics_row(row, row_source)
        data.append(row)

    return markdown_table(data).set_params(row_sep='markdown',
                                           quote=False).get_markdown()


def format_metrics_row(destination, pull_request):
    destination["Created"] = pull_request["created_at"]

    destination["First Commit"] = to_readable_time(pull_request["first_commit_at"])
    destination["Last Commit"] = to_readable_time(pull_request["last_commit_at"])
    destination["Ready for Review"] = to_readable_time(pull_request["ready_for_review_at"])
    destination["First Feedback"] = to_readable_time(pull_request["first_feedback_at"])
    destination["Approved"] = to_readable_time(pull_request["approved_at"])
    destination["Merged"] = to_readable_time(pull_request["merged_at"])

    destination["First Commit To Production (Hrs)"] = format_duration(pull_request["first_commit_to_production"])
    destination["Code Complete To Production (Hrs)"] = format_duration(pull_request["code_complete_to_production"])
    destination["Feedback Delay (Hrs)"] = format_duration(pull_request["feedback_delay"])
    destination["Code Review Duration (Hrs)"] = format_duration(pull_request["code_review_duration"])
    # destination["Code Review Duration (Hrs)"] = format_duration(pull_request["code_review_duration_with_feedback"])
    destination["Time in Active Development (Hrs)"] = format_duration(pull_request["active_development_duration"])


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
    parser.add_argument('--team', required=True)
    args = parser.parse_args()

    main(args.input, args.output, args.team)
