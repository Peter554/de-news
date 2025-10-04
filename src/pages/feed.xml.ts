import rss from "@astrojs/rss";

import { metadata } from "../metadata.ts";
import utils from "../utils.ts";

export async function GET(context) {
  const articles = await utils.getArticles();
  return rss({
    title: metadata.title,
    description: metadata.description,
    site: context.site,
    items: articles.map((article) => ({
      title: article.title,
      pubDate: article.date.toJSDate(),
      link: `articles/${article.slug}`,
    })),
  });
}
