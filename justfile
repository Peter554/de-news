[default]
_default:
    @just --list

serve:
    bun --bun run dev

fetch-articles date="":
    rm -f article-prompt.md ERROR.md
    uv run scripts/create_article_prompt.py {{ if date != "" { "--date " + date } else { "" } }} > article-prompt.md
    cat article-prompt.md | claude -p --model sonnet
    test ! -f ERROR.md

find-missing-dates:
    uv run scripts/find_missing_article_dates.py
