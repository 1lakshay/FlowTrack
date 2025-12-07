# CodePulse – Smart Function Change Detector
CodePulse is a VS Code extension that prevents runtime crashes by monitoring Python functions for logic changes and warning you when dependent functions may break.

# Why CodePulse Prevents Runtime Crashes
file A.py → function f1()
file B.py → calls f1()

If you modify f1():
Python will NOT warn you
VS Code will NOT warn you
The error appears only at runtime, sometimes in production

## Features
- Detects function logic changes using hashing  
- Traces dependency graph automatically  
- Alerts you via Status Bar + Expandable panel  
- Supports watching multiple folders  
- Helps prevent hidden runtime errors

## How to use
- Add folders/files to watch using VS Code Settings:
Settings → Search “CodePulse” → Add Python directories to `codePulse.watchFiles`
- Now just simple do your work, and CodePulse will be workign along with you to make your development go smooth.
- Status bar alert will appear to give a expandable panel with affected functions.

# Limitations
This is an early version. Please note:
Only function-level tracking is supported (Python-only)
Class methods, decorators, inheritance logic NOT analysed yet(Will be added in future releases)
Does not guarantee catching all complex runtime behaviors
This extension is meant as a helper, not a full static analyzer.