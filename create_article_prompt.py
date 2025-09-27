# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pydantic",
# ]
# ///


import json

import pydantic


class ArticleSentence(pydantic.BaseModel):
    text: str
    translated_text: str


class ArticleKeyVocab(pydantic.BaseModel):
    term: str
    translated_term: str
    example_usage: str


class ArticleTag(pydantic.BaseModel):
    name: str
    translated_name: str


class ArticleSource(pydantic.BaseModel):
    name: str
    link_url: str


class Article(pydantic.BaseModel):
    title: str
    translated_title: str
    text: list[ArticleSentence]
    key_vocab: list[ArticleKeyVocab]
    tags: list[ArticleTag]
    sources: list[ArticleSource]


article_schema = Article.model_json_schema()

prompt = f"""\
Search the internet for today's top news.

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
  * Where appropriate, reuse existing tags from the global `tags.json` file.
  * Make sure all the article tags are added to the global `tags.json` file. The file should be sorted alphabetically by tag name.
* Provide links to the original source articles, where one could go to read more.
  * Make sure these links point to specific articles, not generic sites.

For each article, create a JSON file for the result under `articles/$today`, where `$today` is today's date (ISO format).
Each JSON file should obey the schema given below:

```json
{json.dumps(article_schema, indent=2)}
```

Make your changes on a new branch. Commit your changes and open a PR. Assign Peter554 to review the PR.
"""

print(prompt)
