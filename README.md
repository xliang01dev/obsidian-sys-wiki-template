# ArchForge

A self-healing personal knowledge wiki - architecture patterns, tradeoffs, failure modes, and case studies. Heavily inspired by [Andrej Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): the idea that an LLM can act as a compiler, turning raw source material into a structured, interlinked, and self-correcting knowledge base that compounds over time.

## Why Claude + Obsidian + Git

**Obsidian** is more than a Markdown editor - it is a knowledge graph. Every `[[wikilink]]` is a typed edge between concepts, and Obsidian's [Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) exposes that graph to Claude via MCP. This means Claude doesn't just see file contents; it sees backlinks, forward links, orphan nodes, and the full relationship structure of the vault. That graph awareness lets Claude infer where new content belongs, detect when a concept is duplicated across pages, and resolve conflicts by understanding which page is the canonical home for an idea.

**Git** provides versioned, auditable history of every synthesis decision. Every ingest and repair is a commit - the knowledge base is a codebase.

**The self-healing loop:** running `/wiki-doctor` triggers a repair pass that finds broken links, orphaned pages, missing cross-references, and conflicting claims. Each pass leaves the wiki more internally consistent than before. Run it regularly and the wiki converges toward a clean, well-connected knowledge graph rather than drifting into quiet inconsistency as it grows.

---

Source material lives in `raw/`; synthesized knowledge lives in `wiki/`. Claude Code skills keep the two in sync.

## Prerequisites

Install the following tools before proceeding:

- [direnv](https://direnv.net/docs/installation.html) - shell extension that loads `.env` automatically when you enter the project directory
- [Obsidian](https://obsidian.md/) - the note-taking app this vault runs inside
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/getting-started) - the CLI used to run the wiki skills

## 1. direnv setup

direnv automatically loads `.env` into your shell when you enter the project directory.

**1. Add the shell hook** - follow the [direnv hook setup guide](https://direnv.net/docs/hook.html) for your shell (zsh, bash, fish, etc.), then restart your shell.

**2. Enable `.env` loading** - add this to `~/.config/direnv/direnv.toml` (create the file if it doesn't exist):

```toml
[global]
load_dotenv = true
```

**3. Allow direnv in this repo:**

```bash
cd /path/to/this/repo
direnv allow
```

## 2. Obsidian setup

### Open the vault

1. Launch Obsidian
2. Click **Open folder as vault**
3. Select the root of this repository

Obsidian must be running with the vault open whenever you use the Claude Code skills - the MCP server connects to the running Obsidian instance.

### Install the Local REST API plugin

The MCP integration uses the [Obsidian Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) community plugin.

1. In Obsidian, go to **Settings → Community plugins**
2. Disable Safe mode if prompted
3. Click **Browse** and search for **Local REST API**
4. Install and enable it
5. Go to **Settings → Local REST API** and enable **"Enable Non-Encrypted (HTTP) Server"** - the HTTPS server uses a self-signed certificate that MCP clients cannot verify, so HTTP is required
6. Note your **API key** and **port** (default HTTP port: `27123`)

It's recommended that each vault has its own port. If multiple vaults have the same port, then the MCP server may only list the first vault that's associated with the port.

## 3. Configure .env

Copy the sample file and fill in your values:

```bash
cp .env.sample .env
```

Edit `.env`:

```dotenv
PROTOCOL=http
HOST=127.0.0.1
PORT=27123
OBSIDIAN_API_KEY=your-api-key-here
```

Get the API key from **Obsidian → Settings → Local REST API**. The port shown there must match `PORT`.

## 4. Verify the MCP connection

Start a Claude Code session in the repo root:

```bash
claude
```

Claude Code reads `.mcp.json` and connects to Obsidian automatically on startup. To confirm the connection is live, run inside the session:

```
/mcp
```

You should see `obsidian` listed with a **connected** status. If it shows an error or is absent:

- Confirm Obsidian is running with the vault open
- Confirm **"Enable Non-Encrypted (HTTP) Server"** is checked under **Settings → Local REST API**
- Confirm `OBSIDIAN_API_KEY` in `.env` matches the key shown in the plugin settings
- Confirm `PORT` in `.env` matches the port shown in the plugin settings
- Run `direnv allow` again if you recently edited `.env`, then restart the `claude` session

## Workflow

All skills run inside a Claude Code session. Start one in the repo root if you haven't already:

```bash
claude
```

### Add source material

Drop source material into `raw/` - book chapters, article clippings, paper notes, transcripts. Any format is accepted, but Markdown is preferred: it significantly reduces token usage compared to PDFs and other rich formats, which lowers cost and speeds up ingestion. Don't edit existing files under `raw/` as these are used for source material.

### Ingest into the wiki

```
/wiki-ingest
```

Reads new or changed files in `raw/`, updates existing canonical `wiki/` pages where possible, and creates new pages only when the concept is genuinely new. Source files are preserved as evidence.

### Lint and repair

```
/wiki-doctor
```

Checks for broken wikilinks, orphan pages, duplicate content, and missing cross-links. Applies safe structural fixes automatically and flags anything that needs manual review.

### Ask questions

```
/wiki-query
```

Answers questions from the compiled `wiki/` knowledge base. Uses `raw/` as supporting evidence only when the wiki is incomplete. Surfaces gaps and conflicts instead of overclaiming.

## Folder structure

| Folder | Purpose |
|---|---|
| `raw/` | Source material - clippings, chapters, transcripts. Never overwrite with conclusions. |
| `wiki/` | Durable synthesized knowledge - one canonical page per concept. |
| `inbox/` | Temporary capture for unprocessed notes. Triage into `raw/` or `wiki/`. |
| `templates/` | Note templates - structure only, no content. |
| `maintenance/` | Dated lint and repair logs. |
| `output/` | Generated exports. Not the source of truth. |

### Index files

Each folder contains an `index.md` that serves as a directory and entry point for that folder's contents. The skills read these indexes to understand the current state of the vault before making changes.

| Index | What it tracks |
|---|---|
| `wiki/index.md` | All canonical wiki pages, organized by domain - the main table of contents for the knowledge base |
| `raw/index.md` | All source files with a one-line summary of what each produced (which wiki pages were created or updated) |
| `maintenance/index.md` | All dated lint and repair reports in reverse-chronological order with a one-line summary of each run |
