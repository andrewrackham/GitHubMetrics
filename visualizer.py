import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

Path("charts").mkdir(exist_ok=True)


def load_metrics(path):
    with open(path) as f:
        return json.load(f)


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


def main():
    metrics = load_metrics("data/metrics.json")
    df = pd.DataFrame(metrics)
    plot_merge_time_distribution(df)
    plot_prs_by_author(df)
    print("Charts saved to /charts")


if __name__ == "__main__":
    main()
