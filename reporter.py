import argparse
import json


def main(input_file, output_file):
    metrics = load_metrics(input_file)

    with open(output_file, 'w') as f:
        f.write("# GitHub PR Metrics Report\n\n")

        f.write("## Overall Stats\n")
        for key, value in metrics['overall'].items():
            f.write(f"- **{key}**: {value}\n")

        f.write("\n## Per User Stats\n")
        for user, data in metrics['by_user'].items():
            f.write(f"### {user}\n")
            for k, v in data.items():
                f.write(f"- {k}: {v}\n")

        f.write("\n## Per Team Stats\n")
        for team, data in metrics['by_team'].items():
            f.write(f"### {team}\n")
            for k, v in data.items():
                f.write(f"- {k}: {v}\n")


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
