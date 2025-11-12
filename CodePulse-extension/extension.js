const vscode = require("vscode");
const { exec } = require("child_process");
const path = require("path");

function activate() {
  const ws = vscode.workspace.workspaceFolders?.[0];
  if (!ws) return;

  const script = path.join(ws.uri.fsPath, "main.py");

  vscode.workspace.onDidSaveTextDocument((doc) => {
    // only run when "code_to_parse.py" is saved
    if (doc.fileName.endsWith("code_to_parse.py")) {
      exec(`python "${script}"`, (err, stdout, stderr) => {
        if (err) {
          vscode.window.showErrorMessage(`CodePulse error: ${err.message}`);
          return;
        }

        // ✅ Log the output for debugging
        console.log("PYTHON OUTPUT:\n", stdout);

        // 🧩 Skip analysis if Python reports invalid syntax
        if (stdout.includes("SYNTAX_INVALID")) {
          console.log("⏸️ Skipped run: file syntax invalid (user still typing).");
          return;
        }

        // ✅ Look for the NOTIFY_FUNCTIONS marker
        const match = stdout.match(/NOTIFY_FUNCTIONS:\s*(\[.*\])/);
        if (match) {
          try {
            const functions = JSON.parse(match[1]);
            console.log("Detected functions:", functions);

            if (functions.length > 0) {
              const prettyList = functions.map(f => `• ${f}`).join("\n");

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
    }
  });

  vscode.window.showInformationMessage("✅ CodePulse initialized and monitoring saves.");
}

function deactivate() {}

module.exports = { activate, deactivate };
