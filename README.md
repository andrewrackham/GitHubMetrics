# GitHub PR Metrics

## Setup
1. Create a `.env` file with your GitHub token:
```
GITHUB_TOKEN=your_token_here
```

2. Create a `config/teams.yml` file, using `config/teams.template.yml`

## Usage
Run each stage separately:
```bash
docker-compose run github-metrics python collector.py --repo my-org/my-repo --start 2024-01-01 --end 2024-12-31
docker-compose run github-metrics python analyzer.py --input data/raw.json --teams config/teams.yaml
docker-compose run github-metrics python visualizer.py --input data/metrics.json --output-dir charts --team TeamNameA
docker-compose run github-metrics python reporter.py --input data/metrics.json --output report.md --team TeamNameA
```