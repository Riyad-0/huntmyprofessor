import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import scrapeLoginPage from "./loginPage";
import ScrapeError from "./scrapeError";
import signIn from "./signIn";
import searchByProfessor from "./searchByProfessor";
import test from "./test";

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

app.get("/api/test", (req, res) => {
  const ck = test();
  console.log(ck);
  res.json({ ck });
});

app.post("/api/login", async (req, res) => {
  const username = req.body.username;
  const password = req.body.password;
  if (typeof username !== "string" || typeof password !== "string") {
    res.json({
      result: "Error: expected username and password in request."
    });
    return;
  }
  try {
    const scrapeLoginPageResult = await scrapeLoginPage();
    const signInResult = await signIn(
      scrapeLoginPageResult.cookie,
      username,
      password,
      scrapeLoginPageResult.pInstance,
      scrapeLoginPageResult.pPageSubmissionId,
      scrapeLoginPageResult.pPageItemsProtected
    );
    const courses = await searchByProfessor(
      signInResult.ck,
      signInResult.cookie,
      "washburn, alexander",
      scrapeLoginPageResult.pInstance,
      signInResult.pPageSubmissionId,
      signInResult.pPageItemsProtected
    );
    res.json({
      result: "success",
      courses
    });
  } catch (e) {
    if (e instanceof ScrapeError) {
      res.json({
        result: `Error while web scraping: ${e.message()}`
      });
    } else {
      throw e;
    }
  }
});

app.listen(port, () => console.log(`api: http://localhost:${port}`));