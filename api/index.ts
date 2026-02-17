import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import scrapeLoginPage from "./loginPage";
import ScrapeError from "./scrapeError";
import signIn from "./signIn";

const port = 3000;
const users = ["Adam", "Betty", "Cancer"];

const __filename = fileURLToPath(import.meta.url);

// The path to the folder containing this file.
const __dirname = path.dirname(__filename);

const app = express();

app.use(express.json());

app.get("/api/hello", (req, res) => {
  res.json({ message: "hello!" });
});

app.get("/api/test", async (req, res) => {
  try {
    scrapeLoginPage().then(result =>
      signIn(
        result.cookie,
        
      )
    )
    res.send(await scrapeLoginPage());
  } catch (e) {
    if (e instanceof ScrapeError) {
      res.send(`Error while web scraping: ${e.message()}`);
    } else {
      throw e;
    }
  }
});

app.listen(port, () => console.log(`api: http://localhost:${port}`));