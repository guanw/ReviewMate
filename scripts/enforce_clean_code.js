#!/usr/bin/env node
const fs = require("fs");

function analyzeCodeChanges() {
  console.log("Analyzing code changes for Clean Code principles...");

  const violations = [];

  const jsFiles = ["sample.js"];
  for (const file of jsFiles) {
    try {
      const lines = fs.readFileSync(file, "utf8").split("\n");
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].includes("// TODO")) {
          violations.push(
            `TODO found in ${file} (line ${i + 1}): ${lines[i].trim()}. Address technical debt.`,
          );
        }
      }
    } catch (err) {
      // File not found, skip
    }
  }

  if (violations.length > 0) {
    console.log("Clean Code violations found:");
    for (const violation of violations) {
      console.log(`- ${violation}`);
    }
    process.exit(1);
  } else {
    console.log("No Clean Code violations found.");
    process.exit(0);
  }
}

if (require.main === module) {
  analyzeCodeChanges();
}

module.exports = { analyzeCodeChanges };
