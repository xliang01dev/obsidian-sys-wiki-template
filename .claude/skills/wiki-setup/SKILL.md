---
name: wiki-setup
description: Step-by-step installation guide for this wiki vault. For each dependency, checks if it is already installed, explains what it is and what it does, provides install instructions if needed, verifies the result, then moves to the next step. Never installs anything automatically.
---

# Wiki Setup

Walk the user through installing every dependency one step at a time. For each tool:

1. Check whether it is already installed or configured.
2. If already set up: confirm it and move on.
3. If not set up: explain what the tool is and what it does, then provide the install instructions for the user to run themselves.
4. After the user signals they have completed the step, verify it succeeded before continuing.

Never run install commands yourself. Never skip a verification. Never move to the next step until the current one is confirmed. Always run checks one at a time — never batch multiple steps in parallel. Before running any check, tell the user what you are about to check and why.

---

## Reference — OS detection and app checks

Use this section whenever a step needs to verify whether a tool or app is installed. Always detect the OS first, then apply the appropriate check type.

**Step 1 — Detect the OS:**
```bash
uname -s 2>/dev/null || echo "Windows"
```
Returns `Darwin` (macOS), `Linux`, or falls back to `Windows` if `uname` is unavailable.

**Step 2 — Check if the app is installed:**

Always try the CLI (PATH) check first. If not found, try the GUI app check. If found by either, the app is installed.

**CLI check** — try first:

| OS | Command |
|----|---------|
| macOS / Linux | `command -v <appname> && echo "found" \|\| echo "missing"` |
| Windows (cmd) | `where <appname>` |
| Windows (PowerShell) | `Get-Command <appname> -ErrorAction SilentlyContinue` |

**GUI app check** — try if CLI check returns missing:

| OS | Command |
|----|---------|
| macOS | `ls /Applications/<AppName>.app 2>/dev/null && echo "installed" \|\| echo "missing"` |
| Linux | not applicable — GUI apps installed via snap/flatpak/deb are on PATH and found by the CLI check |
| Windows | `test -f "$LOCALAPPDATA/<AppName>/<AppName>.exe" && echo "installed" \|\| echo "missing"` |

Substitute the actual app name for `<appname>` / `<AppName>` based on the step being run.

---

## Step 1 — Node.js

**Check:**
```bash
node --version
```

**What it is:** JavaScript runtime that powers the npm package manager.
**Why it is needed:** qmd is distributed as an npm package and requires Node.js v18 or later to run.

- If v18+ is found: confirm the version and move to Step 2.
- If missing or below v18: explain the above and tell the user to download Node.js v18+ from https://nodejs.org/en/download. After they signal it is installed, re-run `node --version` to verify before continuing.

---

## Step 2 — direnv

**What it is:** A shell extension that automatically loads `.env` into your shell environment whenever you enter a directory that contains one.
**Why it is needed:** The vault stores connection credentials in `.env`. direnv ensures those values are available in the shell before Claude Code starts, without you having to export them manually each time.

**Check:** Follow [OS detection and app checks](#reference--os-detection-and-app-checks) to check if `direnv` is installed.

- If found: move to sub-step 2a.
- If missing: tell the user to install direnv by following https://direnv.net/docs/installation.html and to add the shell hook for their shell (https://direnv.net/docs/hook.html). After they confirm installation, re-run the check to verify.

**Sub-step 2a — direnv.toml config:**

Check whether `load_dotenv = true` is already set:
```bash
cat ~/.config/direnv/direnv.toml 2>/dev/null
```

- If `load_dotenv = true` is present: confirm and move to sub-step 2b.
- If missing or the file does not exist: tell the user to add the following to `~/.config/direnv/direnv.toml` (creating the file if it does not exist):
```toml
[global]
load_dotenv = true
```
After they confirm, re-read the file to verify the value is present.

**Sub-step 2b — Allow direnv in this repo:**

Check:
```bash
direnv status
```

- If the current directory is already allowed: confirm and move to Step 3.
- If not allowed: tell the user to run `direnv allow` in the repo root. After they confirm, re-run `direnv status` to verify. Remind them that `direnv allow` must be re-run any time `.env` is changed.

---

## Step 3 — Claude Code

Claude Code is already running — this step is complete by definition. Confirm this to the user and move on.

---

## Step 4 — Obsidian

**What it is:** The note-taking app this vault runs inside. The Local REST API plugin exposes Obsidian's knowledge graph to Claude over HTTP — Claude sees backlinks, forward links, and orphan nodes, not just file contents.
**Why it is needed:** Obsidian must be running with the vault open whenever Claude Code skills are active. The MCP server connects to the running Obsidian instance.

This step is manual. Guide the user through each sub-step and wait for confirmation before moving on.

**Sub-step 4a — Install Obsidian:**

Follow [OS detection and app checks](#reference--os-detection-and-app-checks) to check if Obsidian is installed.

- If installed: confirm and tell the user to open this repo as a vault if not already open (**File → Open folder as vault → select the repo root**). Ask them to confirm the vault is open, then move to sub-step 4b.
- If missing: tell the user to download and install Obsidian from https://obsidian.md/, then open this repo as a vault. Ask them to confirm when done.

**Sub-step 4b:** Tell the user to go to **Settings → Community plugins**, disable Safe mode if prompted, click **Browse**, search for **Local REST API**, and install and enable it. Ask them to confirm when done.

**Sub-step 4c:** Tell the user to go to **Settings → Local REST API** and enable **"Enable Non-Encrypted (HTTP) Server"**. Explain that HTTP is required because MCP clients cannot verify the self-signed HTTPS certificate. Ask them to confirm when done.

**Sub-step 4d:** Tell the user to note their **API key** and **port** from **Settings → Local REST API** (default port: `27123`). Remind them that each vault should use its own port to avoid conflicts. Ask them to share the values so you can use them in the next sub-step.

**Sub-step 4e — `.env` setup:**

Check whether `.env` exists:
```bash
test -f .env && echo "exists" || echo "missing"
```

- If missing: tell the user to run `cp .env.sample .env` to create it from the sample.

Show the user exactly what will be written to `.env` using the API key and port they provided:
```
OBSIDIAN_PROTOCOL=http
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=<port from user>
OBSIDIAN_API_KEY=<key from user>
```

Ask them to open `.env` and fill in these values themselves. After they confirm, verify the values are present:
```bash
grep "OBSIDIAN_" .env
```

---

## Step 5 — @tobilu/qmd

**What it is:** An on-device hybrid search engine for Markdown that combines BM25 keyword search, semantic vector search, and LLM reranking. It ships with a built-in MCP server that Claude queries directly.
**Why it is needed:** qmd finds wiki pages by meaning rather than keyword frequency, so queries like "tail latency" find the right page even if those words never appear in its headings.

**Check:** Follow [OS detection and app checks](#reference--os-detection-and-app-checks) to check if `qmd` is installed.

- If found: move to sub-step 5b.
- If missing: tell the user to install it by running `npm install -g @tobilu/qmd`. After they confirm, re-run the check to verify.

**Sub-step 5b — Register the vault:**

First, detect the collection name this repo should use:
```bash
basename "$PWD"
```

Then check whether that name is already registered:
```bash
qmd status
```

- If the name from `basename "$PWD"` is listed: confirm and move to sub-step 5c.
- If not listed: tell the user to run from the repo root:
```bash
qmd collection add $(basename "$PWD") .
```
After they confirm, re-run `qmd status` to verify the collection appears.

**Sub-step 5c — Index and embed:**

Check whether documents are already indexed:
```bash
qmd status
```

Explain that `qmd update` indexes all Markdown files and `qmd embed` generates semantic embeddings. The first `qmd embed` run downloads a ~270 MB model. Tell the user to run:
```bash
qmd update && qmd embed
```
After they confirm, re-run `qmd status` to verify the document count is non-zero.

**Sub-step 5d — Write `QMD_INSTALL_PATH` to `.env`:**

Tell the user to run the following to append the qmd binary path to `.env` (the check ensures it is only written once):
```bash
grep -q "QMD_INSTALL_PATH" .env || echo "QMD_INSTALL_PATH=$(which qmd)" >> .env
```

Then reload direnv:
```bash
direnv allow
```

Verify:
```bash
grep "QMD_INSTALL_PATH" .env
```

---

## Completion check

Once all steps are done, verify the full `.env` contains all required variables:
```bash
grep -E "OBSIDIAN_PROTOCOL|OBSIDIAN_HOST|OBSIDIAN_PORT|OBSIDIAN_API_KEY|QMD_INSTALL_PATH" .env
```

All five should be present. Then tell the user:

- Obsidian must be running with the vault open before starting each Claude Code session.
- Run `/mcp` inside a Claude Code session to confirm both `obsidian` and `qmd` show a **connected** status.
- Run `/wiki-ingest` to ingest any source material already in `raw/`.
- Run `direnv allow` any time `.env` is updated.
