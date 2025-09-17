import express from "express";
import { exec } from "child_process";
import fs from "fs";
import { v4 as uuid } from "uuid";

const app = express();
app.use(express.json());

app.post("/execute", (req, res) => {
  const { code } = req.body;
  const fileId = uuid();
  const filePath = `/app/${fileId}.js`;

  fs.writeFileSync(filePath, code);

  exec(`node ${filePath}`, { timeout: 5000 }, (error, stdout, stderr) => {
    fs.unlinkSync(filePath);
    if (error) return res.json({ stdout, stderr: error.message });
    res.json({ stdout, stderr });
  });
});

app.listen(8080, () => console.log("Node runtime running on 8080"));
