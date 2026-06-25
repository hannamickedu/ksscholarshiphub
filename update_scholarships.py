name: Update Scholarships Every Monday

on:
  schedule:
    - cron: '0 12 * * 1'
  workflow_dispatch:

jobs:
  update-scholarships:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Check out the site
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install anthropic requests

      - name: Run scholarship updater
        run: python update_scholarships.py
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

      - name: Commit updated data
        run: |
          git config user.name "Scholarship Bot"
          git config user.email "bot@scholarship-hub"
          git add scholarships.json index.html
          git diff --staged --quiet || git commit -m "Weekly scholarship update - $(date +'%B %d, %Y')"
          git push
