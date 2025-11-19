const vscode = require("vscode");
const { exec } = require("child_process");
const path = require("path");

function activate() {
  const ws = vscode.workspace.workspaceFolders?.[0];
  if (!ws) return;

  const workspaceRoot = ws.uri.fsPath;
  const script = path.join(workspaceRoot, "main.py");

  // Read settings
  const config = vscode.workspace.getConfiguration("codePulse");
  let watchFiles = config.get("watchFiles") || [];
  console.log("CodePulse watching:", watchFiles);

  // Convert all watch entries to absolute normalized paths
  const absoluteWatchPaths = watchFiles.map((item) =>
    path.normalize(path.isAbsolute(item) ? item : path.join(workspaceRoot, item))
  );

  console.log("Absolute watch paths:", absoluteWatchPaths);

  vscode.workspace.onDidSaveTextDocument((doc) => {
    const saved = path.normalize(doc.fileName);

    // Check if saved file matches ANY watched file/directory
    const isWatched = absoluteWatchPaths.some((watchPath) => {
      // If watchPath is a directory → match any .py file inside it
      if (
        watchPath.endsWith(path.sep) ||
        !path.extname(watchPath) // no extension → treat as directory
      ) {
        return saved.startsWith(watchPath);
      }

      // Exact file match
      return saved === watchPath;
    });

    if (!isWatched) {
      console.log("Skipped, file not in watch list:", saved);
      return;
    }

    // Build python args for *every* watched file/directory
    const fileArgs = absoluteWatchPaths
      .map((f) => `"${f.replace(/"/g, '\\"')}"`)
      .join(" ");

    const cmd = `python "${script}" ${fileArgs}`;
    console.log("Executing:", cmd);

    exec(cmd, (err, stdout, stderr) => {
      if (err) {
        vscode.window.showErrorMessage(`CodePulse error: ${err.message}`);
        return;
      }

      console.log("PYTHON OUTPUT:\n", stdout);

      if (stdout.includes("SYNTAX_INVALID")) {
        console.log("⏸️ Skipped run: syntax invalid.");
        return;
      }

      // Parse notify output
      const match = stdout.match(/NOTIFY_FUNCTIONS:\s*(\[.*\])/);
      if (match) {
        try {
          const functions = JSON.parse(match[1]);
          if (functions.length > 0) {
            // const prettyList = functions.map((f) => `• ${f}`).join("\n");
            const prettyList = functions
              .map(item => `• ${item.file} → ${item.function}`)
              .join("\n");


            vscode.window.showWarningMessage(
              `🧠 CodePulse detected logic changes\n\nReview affected functions:\n${prettyList}`,
              "OK"
            );

          }
        } catch (e) {
          vscode.window.showErrorMessage("CodePulse: Failed to parse NOTIFY_FUNCTIONS output.");
        }
      }
    });
  });

  vscode.window.showInformationMessage("✅ CodePulse initialized and monitoring saves.");
}

function deactivate() {}

module.exports = { activate, deactivate };
