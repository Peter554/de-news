import { existsSync } from "fs";
import { join } from "path";

const startDate = new Date("2025-09-17");
const endDate = new Date(); // Today

const missingDates: string[] = [];

let date = new Date(startDate);
while (date <= endDate) {
  const dateStr = date.toISOString().split("T")[0];

  if (!existsSync(join("data", "articles", dateStr))) {
    missingDates.push(dateStr);
  }

  date.setDate(date.getDate() + 1);
}

if (missingDates.length === 0) {
  console.log("No missing dates found!");
} else {
  console.log(`Found ${missingDates.length} missing date(s):\n`);
  missingDates.forEach((date) => console.log(date));
}
