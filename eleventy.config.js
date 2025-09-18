const fs = require("fs").promises;
const path = require("path");

const slugify = require("@sindresorhus/slugify").default;
const { DateTime } = require("luxon");

module.exports = function (eleventyConfig) {
  eleventyConfig.addCollection("articles", async (collectionsApi) => {
    // Get all date directories inside articles folder
    const articlesDir = path.join(__dirname, "articles");

    let dateDirectories = await fs.readdir(articlesDir, {
      withFileTypes: true,
    });
    // Filter only directories (ignore files like .gitkeep)
    dateDirectories = dateDirectories.filter(
      (dirent) => dirent.isDirectory() && !dirent.name.startsWith("."),
    );

    // Process each date directory
    const allArticles = [];

    for (const dateDir of dateDirectories) {
      const dateDirPath = path.join(articlesDir, dateDir.name);
      const articleFiles = await fs.readdir(dateDirPath);

      // Get date from directory name (assuming format YYYY-MM-DD)
      const dateStr = dateDir.name;
      const date = DateTime.fromJSDate(new Date(dateStr));

      // Process each article file in this date directory
      for (const articleFile of articleFiles) {
        const articlePath = path.join(dateDirPath, articleFile);
        const articleContent = await fs.readFile(articlePath, "utf-8");
        const article = JSON.parse(articleContent);

        // Add date field to the article
        article.date = date;

        // Add slug
        article.slug = `${date.toISODate()}/${slugify(article.title)}`;

        // Add to the flattened list
        allArticles.push(article);
      }
    }

    // Sort articles by date and then by title
    allArticles.sort((a, b) => {
      if (a.date === b.date) {
        return a.title.localeCompare(b.title);
      }
      return a.date - b.date;
    });

    return allArticles;
  });

  eleventyConfig.addCollection("tags", async (collectionsApi) => {
    const tagsPath = path.join(__dirname, "tags.json");
    const tagsContent = await fs.readFile(tagsPath, "utf-8");
    const tags = JSON.parse(tagsContent);

    tags.sort((a, b) => {
      return a.name.localeCompare(b.name);
    });

    return tags;
  });

  eleventyConfig.addFilter("index", (articles) => {
    return articles.map((article) => {
      return {
        title: article.title,
        translated_title: article.translated_title,
        date: article.date.toISODate(),
        year: article.date.toISODate().slice(0, 4),
        month: article.date.toISODate().slice(0, 7),
        tags: article.tags
          .map((tag) => `${tag.name} ${tag.translated_name}`)
          .join(" "),
        url: `/articles/${article.slug}/`,
      };
    });
  });

  eleventyConfig.addFilter("newestFirst", (articles) => {
    return articles.toSorted((a, b) => {
      if (a.date === b.date) {
        return a.title.localeCompare(b.title);
      }
      return b.date - a.date;
    });
  });

  eleventyConfig.addFilter("date", (v) => {
    return v.toISODate();
  });

  eleventyConfig.addFilter("last7days", (v) => {
    return v.filter(
      (v) => v.date >= DateTime.now().startOf("day").minus({ days: 7 }),
    );
  });

  eleventyConfig.addNunjucksFilter("matchingTag", function (articles, tag) {
    return articles.filter((article) =>
      article.tags.map((tag) => tag.name).includes(tag.name),
    );
  });

  eleventyConfig.addFilter("groupedByDate", (articles) => {
    const grouped = new Map();
    articles.forEach((article) => {
      const date = article.date.toISODate();
      if (!grouped.has(date)) grouped.set(date, []);
      grouped.get(date).push(article);
    });
    return grouped;
  });
};
