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

  // ⭐ Create Status Bar Item
  const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left);
  statusBarItem.command = "codePulse.showDetails";
  statusBarItem.hide();

  // ⭐ Command to show expanded view
  vscode.commands.registerCommand("codePulse.showDetails", async () => {
    if (!statusBarItem._message) return;

    const pressed = await vscode.window.showInformationMessage(
      statusBarItem._message,
      "Dismiss"
    );

    if (pressed === "Dismiss") {
      statusBarItem.hide();
      statusBarItem._message = "";
    }
  });

  vscode.workspace.onDidSaveTextDocument((doc) => {
    const saved = path.normalize(doc.fileName);

    // Match file/directory
    const isWatched = absoluteWatchPaths.some((watchPath) => {
      if (watchPath.endsWith(path.sep) || !path.extname(watchPath)) {
        return saved.startsWith(watchPath);
      }
      return saved === watchPath;
    });

    if (!isWatched) {
      console.log("Skipped, file not in watch list:", saved);
      return;
    }

    // Build Python args
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

      // Extract NOTIFY_FUNCTIONS
      const match = stdout.match(/NOTIFY_FUNCTIONS:\s*(\[.*\])/);

      if (match) {
        try {
          const functions = JSON.parse(match[1]);

          if (functions.length > 0) {

            // ⭐⭐ NEW BLOCK — GROUP BY FILE ⭐⭐
            const grouped = {};
            functions.forEach(({ file, function: fn }) => {
              if (!grouped[file]) grouped[file] = [];
              grouped[file].push(fn);
            });

            let prettyList = "";
            for (const file in grouped) {
              prettyList += `▸ ${file}\n`;       // collapsible arrow
              grouped[file].forEach(fn => {
                prettyList += `   • ${fn}\n`;
              });
              prettyList += "\n";
            }
            // ⭐⭐ END BLOCK ⭐⭐

            // ⭐ Update the status bar
            statusBarItem.text = "🚨 CodePulse Alert";
            statusBarItem.tooltip = "Click to view affected functions";
            statusBarItem._message =
              `🧠 CodePulse detected logic changes\n\n${prettyList}`;

            statusBarItem.show();
          } else {
            statusBarItem.hide();
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
