#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# ///

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BRANCH_NAME = f"merge-conflicting-prs-{datetime.now().strftime('%Y%m%d%H%M%S')}"
TAGS_FILE = "data/tags.json"


def main():
    print("=== Fetching qualifying PRs ===")
    prs = get_qualifying_prs()
    if not prs:
        print("No qualifying PRs found.")
        return

    print(f"Qualifying PRs: {prs}")

    run("git fetch origin")
    print(f"\n=== Creating branch {BRANCH_NAME} from origin/master ===")
    run(f"git checkout -B {BRANCH_NAME} origin/master")

    # Start with master's tags
    all_tags = json.loads(Path(TAGS_FILE).read_text())

    # Track which files have been checked out and by which PR
    checked_out_by: dict[str, int] = {}

    for pr in prs:
        print(f"\n=== Processing PR #{pr} ===")
        sha = get_pr_head_sha(pr)
        print(f"  HEAD: {sha}")

        run(f"git fetch origin {sha}")

        changed_files = get_changed_files(sha)
        if changed_files:
            # Check for conflicts with previously processed PRs
            conflicts = {
                f: checked_out_by[f] for f in changed_files if f in checked_out_by
            }
            if conflicts:
                print("  ERROR: File conflicts detected with earlier PRs:")
                for f, other_pr in conflicts.items():
                    print(f"    {f} (already checked out by PR #{other_pr})")
                print("  Aborting.")
                sys.exit(1)

            print(f"  Checking out {len(changed_files)} files (excluding tags.json):")
            for f in changed_files:
                print(f"    {f}")
                run(f"git checkout {sha} -- {f}")
                checked_out_by[f] = pr
        else:
            print("  No non-tags files changed.")

        pr_tags = get_tags_from_ref(sha)
        all_tags = merge_tags(all_tags, pr_tags)
        print(f"  Tags collected. Running total: {len(all_tags)}")

    print("\n=== Merging and sorting all tags ===")
    all_tags = sort_tags(all_tags)
    Path(TAGS_FILE).write_text(
        json.dumps(all_tags, indent=2, ensure_ascii=False) + "\n"
    )
    print(f"Final tags.json has {len(all_tags)} tags.")

    print("\n=== Committing ===")
    run("git add -A")
    pr_list = ", ".join(f"#{pr}" for pr in prs)
    commit_msg = (
        f"Merge articles from conflicting PRs with unified tags.json\n\n"
        f"PRs included: {pr_list}\n\n"
        f"Merges all article changes from open PRs that pass the netlify\n"
        f"deploy-preview check, and combines tags.json entries into a single\n"
        f"sorted file."
    )
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)

    print("\n=== Pushing and creating PR ===")
    run(f"git push -u origin {BRANCH_NAME}")
    pr_list_body = "\n".join(f"- #{pr}" for pr in prs)
    body = (
        "## Summary\n"
        "Merges all article changes from open PRs that pass the netlify "
        "deploy-preview check, and combines tags.json entries into a single sorted file.\n\n"
        f"## PRs included\n{pr_list_body}"
    )
    subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--title",
            "Merge articles from conflicting PRs",
            "--body",
            body,
        ],
        check=True,
    )

    print("\n=== Closing old PRs ===")
    for pr in prs:
        print(f"  Closing PR #{pr}...")
        run(f"gh pr close {pr}")

    print("\n=== Done ===")


def run(cmd: str, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, shell=True, check=True, capture_output=True, text=True, **kwargs
    )


def get_qualifying_prs() -> list[int]:
    """Get open PR numbers that pass the netlify deploy-preview check."""
    result = run(
        "gh pr list --limit 100 --json number,statusCheckRollup "
        "--jq '[.[] | select(.statusCheckRollup[]? "
        '| select(.context == "netlify/de-news-app/deploy-preview" '
        'and .state == "SUCCESS")) | .number] | sort | .[]\''
    )
    return [int(n) for n in result.stdout.strip().splitlines() if n.strip()]


def get_pr_head_sha(pr: int) -> str:
    result = run(f"gh pr view {pr} --json headRefOid --jq '.headRefOid'")
    return result.stdout.strip()


def get_changed_files(ref: str) -> list[str]:
    result = run(f"git diff --name-only origin/master...{ref}")
    return [f for f in result.stdout.strip().splitlines() if f and f != TAGS_FILE]


def get_tags_from_ref(ref: str) -> list[dict]:
    result = run(f"git show {ref}:{TAGS_FILE}")
    return json.loads(result.stdout)


def merge_tags(base: list[dict], new: list[dict]) -> list[dict]:
    """Merge two tag lists, deduplicating by name."""
    by_name = {t["name"]: t for t in base}
    for t in new:
        by_name[t["name"]] = t
    return list(by_name.values())


def sort_tags(tags: list[dict]) -> list[dict]:
    return sorted(tags, key=lambda t: t["name"])


if __name__ == "__main__":
    main()
