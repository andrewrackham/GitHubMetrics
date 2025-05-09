import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

Path("charts").mkdir(exist_ok=True)


def load_metrics(path):
    with open(path) as f:
        return json.load(f)


def plot_first_commit_to_production(df):
    # plt.figure(figsize=(10, 6))
    # sns.histplot(df["first_commit_to_production"], bins=20, kde=True)
    # plt.title("Distribution of Time to Production (Working Hours)")
    # plt.xlabel("Hours")
    # plt.ylabel("Number of PRs")
    # plt.savefig("charts/first_commit_to_production.png")

    df["merged_at"] = pd.to_datetime(df["merged_at"])
    df = df.sort_values("merged_at")

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x="created_at", y="first_commit_to_production", hue="team", marker="o")
    plt.title("First Commit to Production by Team")
    plt.xlabel("PR Merge Date")
    plt.ylabel("Time to Production (mins)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("charts/first_commit_to_production.png")
    plt.close()


def plot_weekly_comment_count_distribution(metrics: dict, output_dir: str):
    flat_metrics = {
        week: {**data["totals"], "week": week}
        for week, data in metrics.items()
    }

    # data_frame = pd.DataFrame(list(metrics.items()), columns=["week", "data"])
    data_frame = pd.DataFrame(flat_metrics.values())
    # data_frame.index.name = "week"
    # data_frame.reset_index(inplace=True)

    plt.figure(figsize=(10, 6))
    sns.barplot(data=data_frame, x="week", y="comment_count")
    plt.title("Total Comments Per Week")
    plt.xlabel("Week")
    plt.ylabel("Comment Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/weekly_comment_count.png")


# plt.figure(figsize=(10, 6))
# sns.histplot(data_frame["comment_count"], bins=20, kde=True)
# plt.title("Total Comments Per Week")
# plt.xlabel("Comments")
# plt.ylabel("Week Number")
# plt.savefig(f"{output_dir}/weekly_comment_count.png")


def plot_merge_time_distribution(df):
    plt.figure(figsize=(10, 6))
    sns.histplot(df["time_to_merge_hrs"], bins=20, kde=True)
    plt.title("Distribution of Time to Merge (Working Hours)")
    plt.xlabel("Hours")
    plt.ylabel("Number of PRs")
    plt.savefig("charts/merge_time_distribution.png")


def plot_prs_by_author(df):
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x="author", y="time_to_merge_hrs", ci=None)
    plt.title("Average Time to Merge by Author")
    plt.ylabel("Hours")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("charts/merge_time_by_author.png")


def main(metrics_file: str, output_dir: str, team: str, ):
    metrics = load_metrics(metrics_file)
    team_metrics = metrics["teams"][team]

    # pull_request_df = pd.DataFrame(metrics.get("pull_requests"))
    # plot_first_commit_to_production(pull_request_df)
    # plot_merge_time_distribution(pull_request_df)
    # plot_prs_by_author(pull_request_df)

    plot_weekly_comment_count_distribution(team_metrics["per_week"], output_dir)
    print(f"Charts saved to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--team', required=True)
    args = parser.parse_args()

    main(args.input, args.output_dir, args.team)
