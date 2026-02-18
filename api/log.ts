import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import scrapeLoginPage from "./loginPage";
import ScrapeError from "./scrapeError";
import signIn from "./signIn";
import searchByProfessor from "./searchByProfessor";
import test from "./test";
import fs from "fs/promises";

const port = 3000;
const users = ["Adam", "Betty", "Cancer"];

const __filename = fileURLToPath(import.meta.url);

// The path to the folder containing this file.
const __dirname = path.dirname(__filename);
const logFilePath = path.join(__dirname, "log.json");
function log(s: string) {
  fs.writeFile(logFilePath, s);
}

export default log;