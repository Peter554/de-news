#!/usr/bin/env bun

import { z } from "zod";
import { parseArgs } from "util";

const ArticleSource = z.object({
  name: z.string(),
  link_url: z.string(),
});

const ArticleTag = z.object({
  name: z.string(),
  translated_name: z.string(),
});

const ArticleKeyVocab = z.object({
  term: z.string(),
  translated_term: z.string(),
  example_usage: z.string(),
});

const ArticleSentence = z.object({
  text: z.string(),
  translated_text: z.string(),
});

const Article = z.object({
  title: z.string(),
  translated_title: z.string(),
  text: z.array(ArticleSentence),
  key_vocab: z.array(ArticleKeyVocab),
  tags: z.array(ArticleTag),
  sources: z.array(ArticleSource),
});

const { values } = parseArgs({
  args: Bun.argv.slice(2),
  options: {
    date: {
      type: "string",
      default: new Date().toISOString().split("T")[0],
    },
  },
  strict: true,
  allowPositionals: false,
});

const date = values.date!;

const schema = z.toJSONSchema(Article);

const prompt = `Search the internet for top news for the date ${date}.

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
  * Where appropriate, reuse existing tags from the global \`data/tags.json\` file.
  * Make sure all the article tags are added to the global \`data/tags.json\` file. The file should be sorted alphabetically by tag name.
* Provide links to the original source articles, where one could go to read more.
  * Make sure these links point to specific articles, not generic sites.

For each article, create a JSON file for the result under \`data/articles/${date}\`.
Each JSON file should obey the schema given below:

\`\`\`json
${JSON.stringify(schema, null, 2)}
\`\`\`

Make your changes on a new branch.
Once you've made your changes check the site builds by running \`bun --bun run build\`.
Commit your changes and open a PR.
Assign Peter554 to review the PR.



The end goal of this task is to create an open PR with the new articles and any new tags.
IMPORTANT!: If for any reason you are unable to complete this task then create a file \`ERROR.md\` with a description of the error(s) encountered.
`;

console.log(prompt);
