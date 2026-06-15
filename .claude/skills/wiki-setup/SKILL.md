---
name: wiki-setup
description: Step-by-step installation guide for this wiki vault. For each dependency, checks if it is already installed, explains what it is and what it does, runs install commands directly, and verifies the result before moving on.
---

# Wiki Setup

Walk the user through installing every dependency one step at a time. For each tool:

1. Check whether it is already installed or configured.
2. If already set up: confirm it and move on.
3. If not set up: explain what the tool is and what it does, then run the install command.
4. After the command runs, verify it succeeded before continuing.

Never skip a verification. Never move to the next step until the current one is confirmed. Always run checks one at a time — never batch multiple steps in parallel. Before running any check, tell the user what you are about to check and why.

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
- If not allowed: run the following, then re-run `direnv status` to verify. Remind them that `direnv allow` must be re-run any time `.env` is changed.
```bash
direnv allow
```

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

First check if the values are already loaded:
```bash
printenv OBSIDIAN_PROTOCOL OBSIDIAN_HOST OBSIDIAN_PORT OBSIDIAN_API_KEY
```

- If all four lines are non-empty: confirm and move to Step 5.
- If any are missing or empty: proceed below.

Check whether `.env` exists:
```bash
test -f .env && echo "exists" || echo "missing"
```

- If missing: run the following to create it from the sample:
```bash
cp .env.sample .env
```

Show the user exactly what will be written to `.env` using the API key and port they provided:
```
OBSIDIAN_PROTOCOL=http
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=<port from user>
OBSIDIAN_API_KEY=<key from user>
```

Ask them to open `.env` and fill in these values themselves. After they confirm, run `direnv allow` and re-run the `printenv` check to verify all four are now non-empty.

**Sub-step 4f — Verify Obsidian MCP:**

Call `mcp__obsidian__vault_list`. If it returns a file listing, the Obsidian MCP server is live and Step 4 is complete.

If it fails: check that Obsidian is running with the vault open, the HTTP server is enabled, and the port and API key in `.env` match what is shown in Settings → Local REST API.

---

## Step 5 — @tobilu/qmd

**What it is:** An on-device hybrid search engine for Markdown that combines BM25 keyword search, semantic vector search, and LLM reranking. It ships with a built-in MCP server that Claude queries directly.
**Why it is needed:** qmd finds wiki pages by meaning rather than keyword frequency, so queries like "tail latency" find the right page even if those words never appear in its headings.

**Check:** Follow [OS detection and app checks](#reference--os-detection-and-app-checks) to check if `qmd` is installed.

- If found: move to sub-step 5a.
- If missing: run the following, then re-run the check to verify:
```bash
npm install -g @tobilu/qmd
```

**Sub-step 5a — Write `QMD_INSTALL_PATH` to `.env`:**

First check if it is already set:
```bash
printenv QMD_INSTALL_PATH
```

- If a path is returned: confirm and move to sub-step 5b.
- If empty: run the following to append it to `.env`, then reload direnv and verify:
```bash
grep -q "QMD_INSTALL_PATH" .env || echo "QMD_INSTALL_PATH=$(which qmd)" >> .env
```
```bash
direnv allow
```
```bash
printenv QMD_INSTALL_PATH
```

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
- If not listed: run the following, then verify the collection appears and the path is correct:
```bash
(REPO=$(basename "$PWD") && cd .. && qmd collection add "$REPO")
```
Note: qmd resolves the collection path from the current directory, so the command uses a subshell to cd to the parent without changing your working directory.
```bash
qmd status
qmd collection show $(basename "$PWD")
```

**Sub-step 5c — Index and embed:**

Check whether documents are already indexed:
```bash
qmd status
```

Explain that `qmd update` indexes all Markdown files and `qmd embed` generates semantic embeddings. The first `qmd embed` run downloads a ~270 MB model. Run the following, then re-run `qmd status` to verify the document count is non-zero:
```bash
qmd update && qmd embed
```

---

## Completion check

Once all steps are done, verify the env vars are loaded into the shell:
```bash
printenv | grep -E "OBSIDIAN_PROTOCOL|OBSIDIAN_HOST|OBSIDIAN_PORT|OBSIDIAN_API_KEY|QMD_INSTALL_PATH"
```

All five should be present. If any are missing, run `direnv allow` and check again.

Then verify MCP connectivity by telling the user to run `/mcp` in Claude Code and confirm both servers show a **connected** status:

- **obsidian** — connects via the Local REST API plugin. If not connected: confirm Obsidian is running with the vault open and the HTTP server is enabled.
- **qmd** — connects on session start using `QMD_INSTALL_PATH`. If not connected or missing: start a new Claude Code session (the env var is only read at startup).

If either server shows an error or is absent from `/mcp`, troubleshoot before finishing setup.

Then tell the user:

- Obsidian must be running with the vault open before starting each Claude Code session.
- Run `/wiki-ingest` to ingest any source material already in `raw/`.
- Run `direnv allow` any time `.env` is updated.
