#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["pydantic>=2"]
# ///

import argparse
import json
from datetime import date

from pydantic import BaseModel


class ArticleSentence(BaseModel):
    text: str
    translated_text: str


class ArticleKeyVocab(BaseModel):
    term: str
    translated_term: str
    example_usage: str


class ArticleTag(BaseModel):
    name: str
    translated_name: str


class ArticleSource(BaseModel):
    name: str
    link_url: str


class Article(BaseModel):
    title: str
    translated_title: str
    text: list[ArticleSentence]
    key_vocab: list[ArticleKeyVocab]
    tags: list[ArticleTag]
    sources: list[ArticleSource]


parser = argparse.ArgumentParser()
parser.add_argument("--date", default=date.today().isoformat())
args = parser.parse_args()

schema_str = json.dumps(Article.model_json_schema(), indent=2)

prompt = f"""Search the internet for top news for the date {args.date}.

I'm especially interested in:
- Global news
- UK news
- German news
- Berlin & Brandenburg news

Select 3-5 top articles.

For each article:
* Create a simple German text (B1 level text) of roughly 250 words.
* For each sentence in the text, provide an English translation.
* Provide a key vocab list. For each item in the list:
  * If it is a noun, provide the definite article (der/die/das).
  * If it is a verb, provide the infinitive.
  * Provide a sentence with example usage, taken from the article.
* Provide a list of 2-3 tags that describe the topic of the article.
  * The tags will be used to find articles on the same / similar topics.
  * The tags should be of the form "German text (English translation)" e.g. "Gaza-Konflikt (Gaza Conflict)"
  * Where appropriate, reuse existing tags from the global `data/tags.json` file.
  * Make sure all the article tags are added to the global `data/tags.json` file. The file should be sorted alphabetically by tag name.
* Provide links to the original source articles, where one could go to read more.
  * Make sure these links point to specific articles, not generic sites.

For each article, create a JSON file for the result under `data/articles/{args.date}`.
Each JSON file should obey the schema given below:

```json
{schema_str}
```

The German text may contain special characters and quotation marks (e.g. „..." and «...»).
These must be properly escaped in the JSON.
After creating/updating each JSON file, validate it by running `uv run python -m json.tool <file>` and fix any errors.
This includes the tags file.

Make your changes on a new branch.
Once you've made your changes check the site builds by running `bun --bun run build`.
Commit your changes and open a PR.
Assign Peter554 to review the PR.



The end goal of this task is to create an open PR with the new articles and any new tags.
IMPORTANT!: If for any reason you are unable to complete this task then create a file `ERROR.md` with a description of the error(s) encountered.
"""

print(prompt)
