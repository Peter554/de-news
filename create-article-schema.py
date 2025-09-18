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

schema = Article.model_json_schema()

with open("article-schema.json", "w") as f:
    json.dump(schema, f, indent=4)
