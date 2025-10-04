import { Glob } from "bun";

import slugify from "@sindresorhus/slugify";
import { DateTime } from "luxon";

export const getArticles = async () => {
  const files = await Array.fromAsync(
    new Glob("**/*.json").scan({
      cwd: "data/articles",
      absolute: true,
    }),
  );

  const articles = await Promise.all(
    files.map(async (path) => {
      const article = JSON.parse(await Bun.file(path).text());
      const pathParts = path.split("/");
      const date = DateTime.fromJSDate(
        new Date(pathParts[pathParts.length - 2]),
      );
      const slug = `${date.toISODate()}/${slugify(article.title)}`;
      return {
        ...article,
        date,
        slug,
      };
    }),
  );

  return articles.toSorted((a, b) => {
    if (a.date === b.date) {
      return a.title.localeCompare(b.title);
    }
    return b.date - a.date;
  });
};

export const getTags = async () => {
  const tags = await Bun.file("data/tags.json").json();

  return tags.toSorted((a, b) => {
    return a.name.localeCompare(b.name);
  });
};

export default { getArticles, getTags };
