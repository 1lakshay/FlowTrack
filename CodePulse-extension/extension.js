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

  // ⭐ Create status bar item
  const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left);
  statusBarItem.command = "codePulse.showDetails";
  statusBarItem.hide();

  let lastGroupedOutput = "";   // store HTML content for webview

  // ⭐ Register command to open Webview Panel
  vscode.commands.registerCommand("codePulse.showDetails", () => {
    if (!lastGroupedOutput) return;

    const panel = vscode.window.createWebviewPanel(
      "codePulseDetails",
      "CodePulse – Affected Functions",
      vscode.ViewColumn.Beside,
      { enableScripts: true }
    );

    panel.webview.html = getWebviewHtml(lastGroupedOutput);

    panel.onDidDispose(() => {
      statusBarItem.hide();
    });
  });

  vscode.workspace.onDidSaveTextDocument((doc) => {
    const saved = path.normalize(doc.fileName);

    // Check if saved file matches ANY watched file/directory
    const isWatched = absoluteWatchPaths.some((watchPath) => {
      if (watchPath.endsWith(path.sep) || !path.extname(watchPath))
        return saved.startsWith(watchPath);
      return saved === watchPath;
    });

    if (!isWatched) return;

    // Build python args
    const fileArgs = absoluteWatchPaths
      .map((f) => `"${f.replace(/"/g, '\\"')}"`)
      .join(" ");

    const cmd = `python "${script}" ${fileArgs}`;
    console.log("Executing:", cmd);

    exec(cmd, (err, stdout) => {
      if (err) {
        vscode.window.showErrorMessage(`CodePulse error: ${err.message}`);
        return;
      }

      if (stdout.includes("SYNTAX_INVALID")) return;

      // Parse notify output
      const match = stdout.match(/NOTIFY_FUNCTIONS:\s*(\[.*\])/);
      if (match) {
        try {
          const functions = JSON.parse(match[1]);

          if (functions.length > 0) {
            // ⭐ Group output by file
            const grouped = {};
            functions.forEach(({ file, function: fn }) => {
              if (!grouped[file]) grouped[file] = [];
              grouped[file].push(fn);
            });

            // ⭐ Generate Expandable HTML for Webview
            lastGroupedOutput = buildExpandableHtml(grouped);

            // ⭐ Show Status Bar Alert
            statusBarItem.text = "🚨 CodePulse Alert";
            statusBarItem.tooltip = "Click to view affected functions";
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


// ------------------------
// ⭐ HTML for expandable view
// ------------------------
function getWebviewHtml(content) {
  return `
    <html>
    <body style="font-family: sans-serif; padding: 15px;">
      <h2>🧠 CodePulse – Affected Functions</h2>
      ${content}
    </body>
    </html>
  `;
}

// ------------------------
// ⭐ Build expandable sections per file
// ------------------------
function buildExpandableHtml(grouped) {
  let html = "";

  for (const file in grouped) {
    html += `
      <details style="margin-bottom: 10px;">
        <summary style="font-size: 14px; font-weight: bold;">${file}</summary>
        <ul>
          ${grouped[file].map(fn => `<li>${fn}</li>`).join("")}
        </ul>
      </details>
    `;
  }

  return html;
}
