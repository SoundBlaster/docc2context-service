# docc2context

`docc2context` converts DocC archives into deterministic Markdown + a link graph for LLM ingestion.

## Quick start

Clone the repo:

```bash
git clone git@github.com:SoundBlaster/docc2context.git
```

From the repo root:

```bash
swift run docc2context Fixtures/Docc2contextCore.doccarchive --output /tmp/docc2context-out --force --symbol-layout single
open /tmp/docc2context-out/markdown/documentation/docc2contextcore/benchmarkcomparator.md
```

Outputs:
- Markdown files: `/tmp/docc2context-out/markdown/`
- Link graph: `/tmp/docc2context-out/linkgraph/adjacency.json`

## CLI Usage & Options

```bash
docc2context <input-path> --output <directory> [options]
```

### Required Arguments

| Argument | Description |
|----------|-------------|
| `<input-path>` | Path to a DocC bundle directory or `.doccarchive` directory |

### Required Options

| Option | Description |
|--------|-------------|
| `--output <dir>` | Target directory for Markdown + link graph outputs |

### Optional Flags & Options

| Flag | Description | Default |
|------|-------------|---------|
| `-h, --help` | Show help message and exit | — |
| `--force` | Overwrite output directory if it already exists | false |
| `--format <value>` | Output format; only `markdown` is supported | `markdown` |
| `--technology <name>` | Filter symbols by technology/module name (repeatable) | none |
| `--symbol-layout <layout>` | Symbol page output layout: `tree` or `single` | `tree` |
| `--tutorial-layout <layout>` | Tutorial output layout: `chapter` or `single` | `chapter` |

### Examples

**Basic conversion with default settings:**
```bash
docc2context MyDocs.doccarchive --output ./docs-md
```

**Single-page symbol layout (one .md file per symbol):**
```bash
docc2context MyDocs.doccarchive --output ./docs-md --symbol-layout single
```

**Single-page tutorial layout (flat tutorial structure):**
```bash
docc2context MyDocs.doccarchive --output ./docs-md --tutorial-layout single
```

**Filter symbols by technology (module name):**
```bash
docc2context MyDocs.doccarchive --output ./docs-md --technology MyFramework
```

**Multiple technology filters:**
```bash
docc2context MyDocs.doccarchive --output ./docs-md --technology MyFramework --technology OtherModule
```

**Combined options (overwrite existing output, single layouts):**
```bash
docc2context MyDocs.doccarchive --output ./docs-md --force --symbol-layout single --tutorial-layout single
```

### Output Structure

The converter generates:
- **Markdown files** in `<output>/markdown/` organized by documentation category (symbols, articles, tutorials)
- **Link graph** at `<output>/linkgraph/adjacency.json` containing cross-document relationships
- **Structured index** and table of contents for navigation

### Input Requirements

- Input must be a **directory** (either a DocC bundle or a `.doccarchive` directory)
- If you have a `.doccarchive` **file**, extract it first using: `ditto MyDocs.doccarchive MyDocs.doccarchive-extracted`
- The DocC bundle must contain a valid `Info.plist` manifest

## Installation

### From Source (Swift 6.1.2+)

Clone the repository and build locally:

```bash
git clone git@github.com:SoundBlaster/docc2context.git
cd docc2context
swift build -c release
.build/release/docc2context --help
```

### From GitHub Releases

Binary releases are available for macOS (arm64/x86_64) and Linux (x86_64/aarch64):

```bash
# macOS
curl -L https://github.com/SoundBlaster/docc2context/releases/download/v<version>/docc2context-<version>-macos-arm64.tar.gz | tar xz
sudo mv docc2context /usr/local/bin/

# Linux
curl -L https://github.com/SoundBlaster/docc2context/releases/download/v<version>/docc2context-<version>-linux-x86_64.tar.gz | tar xz
sudo mv docc2context /usr/local/bin/
```

## How to test

```zsh
⏺ Bash(swift build -c release 2>&1 | head -50)
  ⎿  [0/1] Planning build
     [1/1] Compiling plugin Swift-DocC Preview
     [2/2] Compiling plugin Swift-DocC
     … +12 lines (ctrl+o to expand)
```

⏺ Now let me test the release app with the available DocC archive:

```zsh
⏺ Bash(./.build/release/docc2context DOCS/INPROGRESS/SpecificationCore.doccarchive --output /tmp/test_release_output 2>&1)
  ⎿  Generated 0 tutorial volume(s), 0 chapter(s), 27 reference article(s), and 455 symbol(s) into /tmp/test_release_output.
```

⏺ Perfect! The release app built successfully and processed the archive. Let me verify the output:

```zsh
⏺ Bash(ls -lah /tmp/test_release_output/ && echo -e "\n=== Generated Files ===" && find /tmp/test_release_output -type f | head -20)
  ⎿  total 0
     drwxr-xr-x@  4 egor  wheel   128B Jan 13 09:45 .
     drwxrwxrwt  10 root  wheel   320B Jan 13 09:45 ..
     … +24 lines (ctrl+o to expand)

⏺ Bash(ls -lah /tmp/test_release_output/linkgraph/ && echo -e "\n=== Link Graph Sample ===" && head -50
      /tmp/test_release_output/linkgraph/adjacency.json)
  ⎿  total 112
     drwxr-xr-x@ 3 egor  wheel    96B Jan 13 09:45 .
     drwxr-xr-x@ 4 egor  wheel   128B Jan 13 09:45 ..
     … +54 lines (ctrl+o to expand)
```

### ⏺ ✅ Release App Test Successful

  The release app (docc2context) successfully processed DOCS/INPROGRESS/SpecificationCore.doccarchive:

  Output Summary:
  - Tutorials: 0
  - Chapters: 0
  - Reference Articles: 27
  - Symbols: 455

  Generated Files:
  - markdown/documentation/ - 455+ markdown files with API documentation
  - linkgraph/adjacency.json - 54KB link graph for LLM context generation
