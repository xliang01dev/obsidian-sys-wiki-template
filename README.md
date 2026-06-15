# Self Healing Wiki Template for System Design

A self-healing personal knowledge wiki for software system design - architecture patterns, tradeoffs, failure modes, and case studies. Heavily inspired by [Andrej Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): the idea that an LLM can act as a compiler, turning raw source material into a structured, interlinked, and self-correcting knowledge base that compounds over time. In practice, that means a wiki that actively maintains its own integrity - detecting broken links, merging duplicate pages, surfacing conflicting claims, and connecting orphan notes on each run. The structure converges toward consistency over time rather than drifting toward entropy.

## Table of contents

- [Why Claude + Obsidian + qmd + Git](#why-claude--obsidian--qmd--git)
- [How to run](#how-to-run)
- [How to install](#how-to-install)
- [How to verify MCP tools](#how-to-verify-mcp-tools)
- [What the folders do](#what-the-folders-mean)

## Why Claude + Obsidian + qmd + Git

In this setup, that loop is driven by Claude reading raw sources and wiki pages via Obsidian's knowledge graph, finding related content by meaning via qmd, writing durable structured updates, and committing every change to Git. Each tool covers a gap the others leave open - together they form a closed loop where raw source material flows in, structured knowledge flows out, and the wiki corrects itself over time.

| Tool | Why |
|---|---|
| [Claude](https://claude.ai/code) | Acts as the compiler - reads raw source material, synthesizes durable wiki pages, detects gaps and conflicts, and repairs structural issues. Persistent skills (`/wiki-ingest`, `/wiki-query`, `/wiki-doctor`) give it repeatable, scoped behaviors so every run is consistent and auditable. |
| [Obsidian](https://obsidian.md/) | More than a Markdown editor - it is a knowledge graph. Every `[[wikilink]]` is a typed edge between concepts, and the [Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) exposes that graph to Claude via MCP. Claude sees backlinks, forward links, orphan nodes, and the full relationship structure of the vault - letting it infer where new content belongs, detect duplicates, and resolve conflicts. |
| [qmd](https://github.com/tobi/qmd) | On-device hybrid search (BM25 + semantic vectors + LLM reranking) with a built-in MCP server that Claude queries directly. Where keyword search surfaces whatever file has the most literal occurrences, qmd surfaces what the query *means* - so `/wiki-query what is tail latency` finds the right page even when "tail latency" never appears in its headings. |
| [Git](https://git-scm.com/) | Versioned, auditable history of every synthesis decision. Every ingest and repair is a commit - the knowledge base is a codebase. |

## How to run

### Step 1 - Add source material

Drop source material into `raw/`:
- Book chapters
- Article clippings
- Paper notes
- Transcripts

Any format is accepted, but Markdown is preferred: it significantly reduces token usage compared to PDFs and other rich formats, which lowers cost and speeds up ingestion.

**Don't edit existing files under `raw/` as these are used for source material.**

### Step 2 - Run Claude Code and pick a command

Start a Claude Code session in the repo root:

```bash
claude
```

Then run `/wiki-ingest`, `/wiki-query`, or `/wiki-doctor` depending on what you need:

| Command | What it does |
|---|---|
| `/wiki-ingest` | • Reads new or changed files in `raw/`<br>• Updates existing canonical `wiki/` pages where possible<br>• Creates new pages only when the concept is genuinely new<br>• Source files are preserved as evidence |
| `/wiki-query` | • Answers questions from the compiled `wiki/` knowledge base<br>• Uses `raw/` as supporting evidence only when the wiki is incomplete<br>• Surfaces gaps and conflicts instead of overclaiming |
| `/wiki-doctor` | • Checks for broken wikilinks, orphan pages, duplicate content, and missing cross-links<br>• Applies safe structural fixes automatically<br>• Flags anything that needs manual review<br>• After substantive changes, re-sync the qmd index: `qmd update && qmd embed` |

## How to install

Choose one:

### Option 1 - Guided install with `/wiki-setup`

Start a Claude Code session in the repo root and run the setup skill:

```bash
claude
```

```
/wiki-setup
```

The skill walks you through each dependency one step at a time - checking what is already installed, explaining what each tool does, and verifying each step before moving on.

### Option 2 - Manual install

| Tool | Description |
|---|---|
| [Node.js](https://nodejs.org/) | JavaScript runtime; required to install qmd via npm (v18 or later) |
| [direnv](https://direnv.net/docs/installation.html) | Shell extension that loads `.env` automatically when you enter the project directory |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code/getting-started) | The CLI used to run the wiki skills |
| [Obsidian](https://obsidian.md/) | The note-taking app this vault runs inside; must be running for the MCP server to connect |
| [@tobilu/qmd](https://github.com/tobi/qmd) | On-device hybrid search engine that powers semantic wiki queries |

#### 1. Node.js: [Download v18+](https://nodejs.org/en/download)

#### 2. direnv

1. [Install](https://direnv.net/docs/installation.html) and add the [shell hook](https://direnv.net/docs/hook.html) for your shell.
2. Add to `~/.config/direnv/direnv.toml` (create if it doesn't exist):
   ```toml
   [global]
   load_dotenv = true
   ```
3. Run (or re-run any time `.env` is updated):
   ```bash
   direnv allow
   ```

#### 3. Claude Code: Follow the [getting started guide](https://docs.anthropic.com/en/docs/claude-code/getting-started)

#### 4. Obsidian

1. [Download](https://obsidian.md/) and open this repo as a vault.
2. Install the **Local REST API** community plugin.
3. Under **Settings → Local REST API**, enable **"Enable Non-Encrypted (HTTP) Server"** (HTTP required; MCP clients cannot verify the self-signed HTTPS cert).
4. Note your **API key** and **port** (default: `27123`); each vault should use its own port.
5. Copy the sample env file:
   ```bash
   cp .env.sample .env
   ```
6. Open `.env` and fill in your values (find the API key and port under **Settings → Local REST API** in Obsidian):
   ```
   OBSIDIAN_PROTOCOL=http
   OBSIDIAN_HOST=127.0.0.1         # IP where Obsidian is running; 127.0.0.1 if local
   OBSIDIAN_PORT=27123             # Settings → Local REST API → Port
   OBSIDIAN_API_KEY=abcdefg-123456 # Settings → Local REST API → API Key
   ```

#### 5. @tobilu/qmd

1. [Download](https://github.com/tobi/qmd).
2. Register the vault as a qmd collection:
   ```bash
   (REPO=$(basename "$PWD") && cd .. && qmd collection add "$REPO")
   ```
3. Index and embed the vault (downloads a ~270 MB model on first run; re-run after large ingests):
   ```bash
   qmd update && qmd embed
   ```
4. Add to `.env`:
   ```bash
   grep -q "QMD_INSTALL_PATH" .env || echo "QMD_INSTALL_PATH=$(which qmd)" >> .env
   ```

## How to verify MCP tools

Start a Claude Code session in the repo root:

```bash
claude
```

Claude Code reads `.mcp.json` on startup. It connects to Obsidian over HTTP and launches `qmd mcp` as a stdio subprocess - both happen automatically, provided the env vars in `.env` are loaded by direnv before `claude` starts. To confirm both connections are live, run inside the session:

```
/mcp
```

You should see both `obsidian` and `qmd` listed with a **connected** status.

**If `obsidian` shows an error:**
- [ ] Confirm Obsidian is running with the vault open
- [ ] Confirm **"Enable Non-Encrypted (HTTP) Server"** is checked under **Settings → Local REST API**
- [ ] Confirm `OBSIDIAN_API_KEY` in `.env` matches the key shown in the plugin settings
- [ ] Confirm `OBSIDIAN_PORT` in `.env` matches the port shown in the plugin settings
- [ ] Run `direnv allow` again if you recently edited `.env`, then restart the `claude` session

**If `qmd` shows an error:**
- [ ] Confirm `qmd status` runs without error from the repo root
- [ ] Confirm the collection name matches your repo's directory name (run `basename "$PWD"` from the repo root to check)
- [ ] Confirm the binary path in `.mcp.json` is correct (`which qmd` to verify)

## What the folders do

| Folder | Purpose |
|---|---|
| `raw/` | Source material - clippings, chapters, transcripts. Never overwrite with conclusions. |
| `wiki/` | Durable synthesized knowledge - one canonical page per concept. |
| `inbox/` | Temporary capture for unprocessed notes. Triage into `raw/` or `wiki/`. Created on first use. |
| `templates/` | Note templates - structure only, no content. |
| `maintenance/` | Dated lint and repair logs. |
| `output/` | Generated exports on request. Not the source of truth. Created on first use. |

### Index files

Each folder contains an `index.md` that serves as a directory and entry point for that folder's contents. The skills read these indexes to understand the current state of the vault before making changes.

| Index | What it tracks |
|---|---|
| `wiki/index.md` | All canonical wiki pages, organized by domain (scaling, data tier, distributed systems, case studies, etc.) - the main table of contents for the knowledge base |
| `raw/index.md` | All source files and subfolders with a one-line summary of what each produced (which wiki pages were created or updated) |
| `maintenance/index.md` | All dated lint and repair reports in reverse-chronological order with a one-line summary of each run |
