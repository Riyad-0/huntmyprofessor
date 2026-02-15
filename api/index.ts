import express from "express";
import path from "path";
import { fileURLToPath } from "url";

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

app.listen(port, () => console.log(`api: http://localhost:${port}`));