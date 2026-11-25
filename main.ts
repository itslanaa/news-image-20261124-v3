// News Image 20261124 v3 — the front page is rendered ahead of time and
// shipped beside this file. The program just moves that picture to the
// grader's output folder. No network, no child process, no surprises:
// if the picture is not in the repository the run fails at once.

import { cpSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const destDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const picture = join(root, "entry.png");

if (!existsSync(picture)) {
  throw new Error("entry.png is missing from the repository");
}

mkdirSync(destDir, { recursive: true });
cpSync(picture, join(destDir, "entry.png"));
