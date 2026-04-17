---
name: system-type-cli-tool
description: "Domain patterns for CLI tools and developer SDKs — command structure, configuration layering, plugin architecture, distribution, backward compatibility, shell integration, and failure modes. Use when designing or evaluating command-line tools, developer platforms, or SDK libraries."
---

# System Type: CLI Tool & Developer SDK

Patterns, failure modes, and anti-patterns for command-line tools and developer-facing libraries.

---

## Command Structure Patterns

### Subcommand Trees (git-style)
**What it is.** Top-level command dispatches to subcommands, each with its own flags and arguments. `tool <subcommand> [flags] [args]`. The dominant pattern for non-trivial CLIs.
**When to use.** Tools with more than ~5 distinct operations. When operations have different flag sets. When you want discoverability — `tool help` lists all subcommands.
**When to avoid.** Single-purpose tools that do one thing (e.g., `curl`, `jq`). Adding subcommands to a tool that does one thing well makes it do many things poorly.
**Nesting depth.** Two levels (`tool resource action`) is the practical limit. Three levels (`tool group resource action`) works if the grouping is obvious (e.g., `kubectl get pods`). Four levels means your CLI needs a redesign.

### Flag Conventions
**POSIX short flags.** Single dash, single letter: `-v`, `-f`. Combinable: `-vvv` for verbosity levels, `-rf` for multiple flags. Every short flag should have a long equivalent.
**GNU long flags.** Double dash, full words: `--verbose`, `--output-format`. Self-documenting. Use hyphens, not underscores.
**Boolean flags.** `--color` enables, `--no-color` disables. Pick a sensible default and provide the negation. Don't require `--color=true`.
**Value flags.** `--output json` or `--output=json`. Support both forms. Be consistent across all flags.
**The `--` separator.** Everything after `--` is a positional argument, not a flag. Mandatory for tools that accept arbitrary user input — without it, `tool delete --force` is ambiguous (is `--force` a flag or an argument?).

### Positional Arguments vs. Flags
**Positional args** are for the primary noun — the thing being operated on. `tool build ./src`, `tool deploy production`. One or two positional args maximum. After that, you need flags.
**Flags** are for everything that modifies behavior. If the user could reasonably forget to provide it and get a useful default, it's a flag, not a positional arg.
**Rule of thumb.** If you're reading the help text to remember which positional arg is which, they should be flags.

### Global vs. Local Flags
**Global flags** apply to every subcommand: `--verbose`, `--config`, `--output-format`, `--no-color`. Define them once at the root. They should be few and genuinely universal.
**Local flags** belong to a specific subcommand. Don't pollute the global namespace with flags only one subcommand uses.

### Interactive Prompts vs. Flags
**Interactive prompts** are for first-run setup, destructive confirmations, and guided workflows (`tool init`). Always provide a flag equivalent (`--yes`, `--name=foo`) so scripts can bypass prompts.
**TTY detection.** If stdin is not a TTY, never prompt. Fail with an actionable error telling the user which flag to pass. A CI pipeline hanging on a prompt is a production incident.

### stdin/stdout/stderr Discipline
**stdout** is for program output — the data the user asked for. It must be parseable. If someone pipes your output, only the data should flow through.
**stderr** is for human messages — progress indicators, warnings, debug info, error messages. Everything that isn't the requested data.
**stdin** is for data input. Accept `-` as a filename to mean stdin. Support piping: `cat file | tool process` and `tool process < file`.
**The test.** `tool list | wc -l` should return a correct count. If your progress spinner or status message contaminates stdout, you've broken the Unix contract.

## Configuration Layering

### The Hierarchy
Highest precedence wins. The standard order:

1. **Command-line flags.** Always win. The user is explicitly telling you what to do right now.
2. **Environment variables.** Useful for CI, containers, and temporary overrides. Convention: `TOOLNAME_FLAGNAME` (e.g., `GIT_AUTHOR_NAME`).
3. **Project config.** `.toolrc`, `tool.toml`, or a section in `pyproject.toml` / `package.json`. Checked in to version control. Shared by the team.
4. **User config.** `~/.config/tool/config.toml` (XDG) or `~/.toolrc`. Personal preferences that apply across all projects.
5. **System config.** `/etc/tool/config.toml`. Org-wide defaults set by admins. Rare in practice.
6. **Compiled defaults.** The values your code uses when nothing else is specified.

Every layer is optional. Missing layers are silently skipped. The tool works with zero configuration.

### XDG Base Directory Spec
**Config:** `$XDG_CONFIG_HOME/tool/` (default `~/.config/tool/`). User settings.
**Data:** `$XDG_DATA_HOME/tool/` (default `~/.local/share/tool/`). Persistent data the user didn't explicitly create (caches of fetched schemas, downloaded plugins).
**State:** `$XDG_STATE_HOME/tool/` (default `~/.local/state/tool/`). Logs, history, undo state — data that can be deleted without data loss.
**Cache:** `$XDG_CACHE_HOME/tool/` (default `~/.cache/tool/`). Regeneratable data. Safe to delete at any time.
**Why it matters.** Dotfile pollution in `$HOME` is a real problem. Respecting XDG makes your tool a good citizen on Linux. On macOS, `~/Library/Application Support/` is the equivalent convention. On Windows, `%APPDATA%`.

### Config File Formats
**TOML.** Best for CLIs. Human-readable, supports comments, unambiguous types, no indentation wars. Used by Cargo, pip, and most modern Rust/Python CLIs.
**YAML.** Dangerous at scale (Norway problem, implicit type coercion, indentation sensitivity). Acceptable when your ecosystem already uses it (Kubernetes, GitHub Actions). Always use a strict parser.
**JSON.** No comments. Painful to hand-edit. Fine for machine-generated config. Never use for user-facing config files unless you also accept JSON5 or JSONC.
**INI.** Simple but limited — no nested structures, no standard for lists. Acceptable for very simple tools. `git config` makes it work, but git is the exception, not the rule.

### Config Discovery and Merging
**Walk-up discovery.** Search for `.toolrc` starting from the current directory, walking up to filesystem root or `$HOME`. The nearest config wins (or configs are merged, with nearer taking precedence).
**Explicit path.** `--config path/to/config.toml` overrides all discovery. Always support this.
**Debug command.** `tool config show` or `tool config list` should print the resolved configuration with the source of each value (which file, which env var, or default). Without this, config debugging is guesswork.

## Plugin and Extension Architecture

### Plugin Discovery
**PATH-based.** Plugins are executables named `tool-pluginname` on `$PATH`. `tool foo` finds and runs `tool-foo`. Git uses this pattern. Simple, works with any language. Downsides: namespace collisions, no version management, no metadata.
**Directory-based.** Plugins live in a known directory (`~/.tool/plugins/`, or a path set via config). Tool scans the directory at startup. Allows metadata files alongside plugins. Used by kubectl (krew), fish shell.
**Registry-based.** Plugins are declared in a config file or remote registry. Installed explicitly (`tool plugin install foo`). Provides version management, dependency resolution, and discoverability. More complex to implement. Used by Terraform providers, VS Code extensions.

### Plugin API Stability Contracts
**The plugin API is a public API.** Breaking it breaks the ecosystem. Version it from day one.
**Minimal surface area.** Expose the smallest possible interface. Every function you expose is a function you maintain forever. Prefer data exchange (JSON on stdin/stdout, structured file formats) over shared libraries.
**Capability negotiation.** Plugins declare which API version they support. The host checks compatibility before loading. Fail loudly on mismatch: "Plugin X requires API v3, but tool is at v2. Upgrade tool or downgrade plugin."

### Hook Points vs. Full Extensions
**Hook points** are specific lifecycle moments where plugins can inject behavior: pre-commit, post-deploy, on-error. Narrow scope, easy to reason about, low risk of plugins interfering with each other.
**Full extensions** add new subcommands, new output formats, or new resource types. More powerful, but harder to maintain compatibility. Plugins can step on each other — two plugins adding the same subcommand is a conflict you need to handle.
**Start with hooks.** Add full extensions only when hooks are demonstrably insufficient.

## Distribution and Installation

### Package Managers
**Language-native.** `pip install tool`, `npm install -g tool`, `cargo install tool`. Lowest friction for developers already in that ecosystem. Downside: requires the language runtime.
**System-native.** `brew install tool`, `apt install tool`, `choco install tool`. Best for tools that transcend a single language ecosystem. Requires maintaining package definitions for each manager.
**The reality.** Support at least one language-native and one system-native method. Provide a `curl | sh` installer as a fallback. Accept that users will find your installation instructions confusing no matter what you do.

### Single-Binary Distribution
**Why.** No runtime dependencies, no version conflicts, trivial installation. Download, chmod +x, run. The gold standard for CLI distribution.
**How.** Go and Rust compile to static binaries by default. Python tools can use PyInstaller or Nuitka (with caveats). Node tools can use pkg or bun compile (with caveats).
**Cross-compilation.** Build for linux/amd64, linux/arm64, darwin/amd64, darwin/arm64, windows/amd64 at minimum. CI matrix builds or cross-compilation toolchains (cross for Rust, GOOS/GOARCH for Go).

### Auto-Update Mechanisms
**Opt-in, not opt-out.** Never update without the user's knowledge. A tool that silently changes behavior between invocations is a tool that can't be trusted in CI.
**Check frequency.** Check for updates at most once per day. Cache the result. Never block startup on an update check — do it in the background or after the command completes.
**Version pinning for CI.** Provide a way to install a specific version: `tool@1.2.3`, `pip install tool==1.2.3`. CI pipelines must be reproducible. `latest` is not a version.

### Cross-Platform Considerations
**Path separators.** Use your language's path library. Never hardcode `/` or `\\`.
**Line endings.** Emit `\n` on all platforms unless you have a specific reason not to. Windows terminals handle `\n` fine; Unix tools choke on `\r\n`.
**Home directory.** Don't hardcode `~`. Use the platform's API to find the home directory.
**File permissions.** Windows doesn't have Unix permissions. Handle this gracefully (skip `chmod` on Windows rather than failing).

## Backward Compatibility

### Your Output Is an API
The most important principle for CLI tools: **people write scripts against your output.** Changing output format is the CLI equivalent of changing a REST API response — it breaks consumers silently.

**Machine-readable output.** Always provide `--output json` (or `--json`). JSON output is your stable API contract. Human-readable output can change between minor versions; JSON output follows semver strictly.
**Structured output contract.** Document the JSON schema. Adding fields is backward-compatible. Removing or renaming fields is a breaking change. Changing the type of a field is a breaking change.
**Table output.** Human-readable tables are for humans. Never promise column positions or exact formatting. If users are parsing your table output with `awk`, give them `--output json` and stop worrying about it.

### Semantic Versioning for CLIs
**Major version (2.0.0).** Breaking changes to: JSON output schema, exit codes, flag names, subcommand names, or config file format.
**Minor version (1.1.0).** New subcommands, new flags, new output fields, new config options. Existing behavior unchanged.
**Patch version (1.1.1).** Bug fixes only.
**The hard part.** Fixing a bug in exit codes is technically a breaking change if anyone depended on the buggy behavior. Use judgment. If the bug was clearly a bug, fix it in a patch. If it was ambiguous, fix it in a minor with a deprecation notice.

### Flag Deprecation Strategy
**Phase 1 (minor version).** Old flag still works. Prints a warning to stderr: "Warning: --old-flag is deprecated, use --new-flag instead. Will be removed in v3.0."
**Phase 2 (next major version).** Old flag is removed. Clear error message: "Error: --old-flag was removed in v3.0. Use --new-flag instead."
**Never silently change flag semantics.** If `--force` meant "skip confirmation" in v1 and you want it to mean "overwrite existing" in v2, that's a new flag with a new name, not a semantic change to an existing flag.

### UI Changes vs. API Changes
**UI (human-facing).** Colors, progress bars, table formatting, help text, error message wording. Can change freely between minor versions.
**API (machine-facing).** Exit codes, JSON output, flag names, environment variable names, config file keys, file paths written to disk. Semver-protected.
**The gray area.** stderr messages that users parse with grep. This is unsupported but common. Provide a structured alternative (`--output json` for errors too) and document that stderr format is not stable.

## Shell Integration

### Completions
**Generate, don't hand-write.** Use your framework's completion generation (cobra, clap, click, argparse). Hand-maintained completions drift from the actual flags.
**Install command.** `tool completion bash > /etc/bash_completion.d/tool` or `tool completion --install`. Make it a one-liner. Document it in `--help`.
**Support bash, zsh, and fish at minimum.** PowerShell if you have Windows users. Each shell has different completion mechanisms — use a library that handles this.

### Exit Codes as API
**0:** Success.
**1:** General error.
**2:** Usage error (bad flags, wrong arguments). The user called the tool wrong.
**Distinguish machine-actionable failures.** If callers need to branch on different error types, assign distinct exit codes and document them. `diff` returns 1 for "files differ" and 2 for "trouble" — callers rely on this distinction.
**Don't go wild.** More than ~10 distinct exit codes is a sign you should use structured error output (`--output json`) instead of encoding error taxonomy in a single integer.
**Never use exit codes above 125.** Shells reserve 126 (command not executable), 127 (command not found), and 128+N (killed by signal N). Your exit codes will collide with these.

### Signal Handling
**SIGINT (Ctrl+C).** Clean up and exit promptly. Don't trap SIGINT to print "are you sure?" — that breaks pipeline behavior. If you need confirmation, use a flag (`--interactive`), not a signal trap.
**SIGTERM.** Graceful shutdown. Finish in-progress writes, clean up temp files, exit. Same as SIGINT for most CLIs.
**SIGPIPE.** Die silently. If the reader of your pipe closes early (`tool list | head -5`), don't print an error. Most languages handle this correctly by default; Python notably does not — add `signal.signal(signal.SIGPIPE, signal.SIG_DFL)`.
**Temp file cleanup.** Use OS-level temp directories and clean up on exit. Register cleanup handlers for signal cases. A tool that leaves temp files on Ctrl+C is a tool that slowly fills disks.

### TTY Detection and Formatting
**Detect the TTY.** `isatty(stdout)` determines whether you're writing to a terminal or a pipe. When piped, disable colors, progress bars, spinners, and interactive formatting.
**Color.** Respect `NO_COLOR` (https://no-color.org/) and `FORCE_COLOR` environment variables. Support `--color=auto|always|never`. Default to `auto` (color when TTY, no color when piped).
**Width.** Use terminal width for wrapping and table layout. Fall back to 80 columns when not a TTY. Don't hard-wrap at 80 when the terminal is 200 columns wide.

## Error Handling and UX

### Progressive Disclosure
**Default output.** Short, actionable error message. One or two lines. Enough to fix the problem in the common case.
**`--verbose`.** Include context: what the tool was trying to do, what it expected, what it got. Include paths, URLs, and relevant config values.
**`--debug`.** Full diagnostic dump: HTTP request/response bodies, config resolution trace, plugin loading order, system info. Intended for bug reports, not normal use.
**Environment variable override.** `TOOL_LOG=debug` or `TOOL_DEBUG=1` as an alternative to `--debug`. Useful when the error occurs before flag parsing.

### Actionable Error Messages
**Bad:** `Error: invalid configuration`
**Good:** `Error: config file ~/.config/tool/config.toml has invalid syntax at line 12: expected string, got integer for field 'timeout'. Run 'tool config validate' to check your configuration.`

**Every error message should answer:** What happened? Why? What should the user do next?

### Typo Suggestions
When the user types `tool biuld`, suggest `tool build`. Levenshtein distance of 1-2 on subcommands and flags. This is table stakes for modern CLIs. Libraries like `clap` and `cobra` provide this out of the box.

### Dry-Run Mode
`--dry-run` shows what the tool would do without doing it. Essential for destructive operations (delete, deploy, migrate). The output should be specific enough that the user can predict exactly what will happen. "Would delete 3 files" is useless. "Would delete: ./a.txt, ./b.txt, ./c.txt" is useful.

### Progress Indicators
**Bounded work:** Progress bars with percentage and ETA. Update no more than ~10 times per second.
**Unbounded work:** Spinners or activity indicators. Show what's currently happening ("Downloading index...", "Resolving dependencies...").
**Output to stderr.** Always. Progress indicators on stdout corrupt pipeable output.
**Non-TTY.** When not a TTY, print milestone lines instead of progress bars: "Downloaded 50/100 packages". Or print nothing — silence is better than a flood of progress lines in a log file.

## Common Failure Modes

- **Breaking output format that scripts depend on.** Changing human-readable output that turns out to be parsed by `awk`/`grep` in CI pipelines. Mitigation: always provide `--output json`, treat JSON schema as semver-protected, document that human output is unstable.
- **Config file conflicts between versions.** v2 writes a config file that v1 can't read, or vice versa. Users with multiple projects on different versions hit this constantly. Mitigation: version the config file format. Be forward-compatible (ignore unknown keys rather than erroring).
- **PATH pollution from plugins.** PATH-based plugin discovery means every `tool-*` binary on PATH is a potential plugin, including unrelated tools. Mitigation: use a plugin directory instead of PATH, or namespace aggressively.
- **Slow startup time.** CLI tools are invoked hundreds of times per day, often in tight loops. A 500ms startup time is a productivity tax. Mitigation: lazy-load heavy dependencies, avoid dynamic plugin scanning on every invocation (cache the scan), consider compiled languages for hot-path tools. Measure startup time in CI.
- **Missing offline support.** Tools that phone home on every invocation, fail without network, or require auth for read-only local operations. Mitigation: cache aggressively, degrade gracefully, separate "needs network" from "works locally".
- **Platform-specific bugs.** Works on macOS, breaks on Linux (or vice versa). Path handling, line endings, locale differences, missing commands (`readlink -f` doesn't work on macOS). Mitigation: CI matrix testing on all supported platforms. Use portable standard library functions instead of shelling out.
- **Locale and encoding assumptions.** Assuming UTF-8 when the system locale is different, or vice versa. Filenames containing spaces, unicode, or special characters breaking argument parsing. Mitigation: always handle bytes or explicitly decode with error handling. Test with adversarial filenames.
- **Conflicting global installs.** Two projects need different versions of the same global tool. Mitigation: support project-local installation (`npx`, `uvx`, `cargo run`), version pinning in project config, lockfiles for tool versions.

## Anti-Patterns

- **The Chatty Default.** Printing banners, tips, version info, and update notices on every invocation. Your tool's output is someone else's input. Default to quiet; let users opt into noise.
- **Flag Salad.** Dozens of top-level flags with no subcommand structure. If `--help` scrolls for three screens, you need subcommands and flag groups.
- **The Unscriptable Tool.** Interactive prompts with no flag equivalents. Colored output with no `--no-color`. Human-readable output with no `--json`. Requires a TTY to function. This tool cannot be used in CI.
- **Silent Failure.** Exiting with code 0 when something went wrong. Tools that claim success but didn't actually do the work. Exit code 0 means success — if it wasn't a success, don't return 0.
- **Config File as Only Interface.** Requiring a config file for basic operations instead of accepting flags. The first invocation should work with zero files on disk. Config files are for persistent preferences, not required inputs.
- **Reinventing the Shell.** Building a REPL when a subcommand would do. Adding shell-like features (history, piping, scripting) inside the tool instead of composing with the actual shell. Unless you're building a database client or interactive debugger, you probably don't need a REPL.
- **Version Gatekeeping.** Refusing to run unless every dependency is the exact right version. Warn about version mismatches; only error on known incompatibilities. Overly strict version checks block users who know what they're doing.
- **The Everything Binary.** Bundling unrelated functionality into one tool because distribution is easier. A tool that does builds, deploys, monitors, and manages infrastructure is four tools wearing a trenchcoat. Separate concerns, share libraries.
- **Undocumented Environment Variables.** Using env vars for configuration without listing them in `--help` or docs. If `TOOL_SECRET_FLAG=1` changes behavior, it must be discoverable. Hidden knobs are untestable knobs.
- **Stdout Pollution.** Mixing data output with status messages, warnings, or diagnostic info on stdout. One warning in stdout breaks every pipeline that parses your output. Status goes to stderr. Always.
