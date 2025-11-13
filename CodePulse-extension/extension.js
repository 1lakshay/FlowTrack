const vscode = require("vscode");
const { exec } = require("child_process");
const path = require("path");

function activate() {
  const ws = vscode.workspace.workspaceFolders?.[0];
  if (!ws) return;

  const script = path.join(ws.uri.fsPath, "main.py");

  // 🧩 Read the list of watched files from VS Code settings
  const config = vscode.workspace.getConfiguration("codePulse");
  let watchFiles = config.get("watchFiles") || [];
  console.log("CodePulse watching files:", watchFiles);

  vscode.workspace.onDidSaveTextDocument((doc) => {
    const fileName = path.basename(doc.fileName);

    // 🛑 Skip if no watch files defined
    if (!watchFiles || watchFiles.length === 0) {
      return;
    }

    // 🛑 Only run when this saved file is in the watch list
    if (!watchFiles.includes(fileName)) {
      return;
    }

    // 🧩 Quote and escape each filename safely
    const fileArgs = watchFiles
      .map((f) => `"${f.replace(/"/g, '\\"')}"`)
      .join(" ");

    // 🧩 Build command: python main.py <file1> <file2> <file3>
    const cmd = `python "${script}" ${fileArgs}`;
    console.log("Executing:", cmd);

    exec(cmd, (err, stdout, stderr) => {
      if (err) {
        vscode.window.showErrorMessage(`CodePulse error: ${err.message}`);
        return;
      }

      console.log("PYTHON OUTPUT:\n", stdout);

      // Skip analysis if syntax is invalid
      if (stdout.includes("SYNTAX_INVALID")) {
        console.log("⏸️ Skipped run: file syntax invalid (user still typing).");
        return;
      }

      // 🧩 Look for NOTIFY_FUNCTIONS in the Python output
      const match = stdout.match(/NOTIFY_FUNCTIONS:\s*(\[.*\])/);
      if (match) {
        try {
          const functions = JSON.parse(match[1]);
          console.log("Detected functions:", functions);

          if (functions.length > 0) {
            const prettyList = functions.map((f) => `• ${f}`).join("\n");

            vscode.window.showWarningMessage(
              `🧠  CodePulse detected logic changes\n\nReview affected functions:\n${prettyList}`,
              "OK"
            );
          } else {
            vscode.window.showInformationMessage("✅ CodePulse: No function changes detected.");
          }
        } catch (e) {
          vscode.window.showErrorMessage("CodePulse: Failed to parse NOTIFY_FUNCTIONS output.");
        }
      } else {
        console.log("No NOTIFY_FUNCTIONS found in output.");
      }
    });
  });

  vscode.window.showInformationMessage("✅ CodePulse initialized and monitoring saves.");
}

function deactivate() {}

module.exports = { activate, deactivate };
