# ⚡ CodePulse – Smart Function Change Detector

CodePulse is a **Visual Studio Code extension** designed to prevent hard-to-catch runtime crashes in Python projects. It automatically monitors changes to Python function logic and alerts you when those changes might break dependent functions elsewhere in your codebase.

[![Marketplace](https://img.shields.io/badge/VS%20Code%20Marketplace-Install-brightgreen.svg)](https://marketplace.visualstudio.com/items?itemName=Lakshay.thecodepulse)
[![GitHub license](https://img.shields.io/github/license/lakshay/CodePulse.svg)](https://marketplace.visualstudio.com/items/Lakshay.thecodepulse/license)

---

## 🛑 The Problem: Hidden Runtime Crashes

Python's dynamic linking often hides errors until the affected code path is executed, leading to unexpected crashes in testing or production.

Consider this common scenario:

* **`file A.py`** contains the function `f1()`
* **`file B.py`** calls `f1()`

If you modify the signature or internal logic of `f1()` in `A.py`, causing it to break its contract:

| Status | Warning |
| :--- | :--- |
| **Python** | ❌ **NO** warning at edit time. |
| **VS Code** | ❌ **NO** warning. |
| **Error** | Appears only at **runtime** when `B.py` is executed. |

**CodePulse proactively intercepts this potential breakage.**

---

## ✨ Features

CodePulse acts as your background development guardian, providing proactive alerts to ensure smooth development:

* **Logic Change Detection:** Uses hashing to precisely detect when a function's core logic has been altered.
* **Automatic Dependency Tracing:** Automatically builds a dependency graph, tracking which functions rely on the modified code.
* **Seamless Alerts:** Provides unobtrusive warnings via the **VS Code Status Bar**.
* **Expandable Panel:** Click the Status Bar alert to view a panel listing all potentially **affected functions** that require your review.
* **Multi-Folder Support:** Easily configure the extension to watch multiple Python source directories in your workspace.
* **Runtime Error Prevention:** Helps developers preemptively fix hidden runtime errors caused by unexpected dependency changes.

---

## 🚀 How to Use

### 1. Installation

Install **CodePulse** directly from the Visual Studio Marketplace.

### 2. Configuration

You need to tell CodePulse which folders contain your Python source files:

1.  Open **VS Code Settings** (`Ctrl+,` or `Cmd+,`).
2.  Search for **“CodePulse”**.
3.  Add the root directories containing your Python code (e.g., `./src`, `./backend`) to the `codePulse.watchFiles` setting.

### 3. Workflow

Now just continue your work as usual. CodePulse works in the background:

* When you modify a function, a **Status Bar alert** will appear if dependent functions are affected.
* Click the status bar alert to open the expandable panel with the full list of files and functions to review.

---

## ⚠️ Limitations (Early Version)

Please note that this is an early release. We are actively working on expanding its capabilities.

* **Python-Only:** Only function-level tracking is currently supported.
* **Scope:** Logic related to **Class methods**, **decorators**, and complex **inheritance logic** is **NOT** analysed yet (Will be added in future releases).
* **Not a Full Analyzer:** This extension is a helper tool and does not guarantee catching all complex runtime behaviors.

---

## 🤝 Contribution

We welcome contributions, feature requests, and bug reports!

**Star** the repository to show your support.


[View Source Code on GitHub](https://github.com/1lakshay/CodePulse)