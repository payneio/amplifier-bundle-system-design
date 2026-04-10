"""Amplifier hook: design-context awareness.

Injects ambient design state into the agent's context before every LLM call:
- Existing design documents in the project (docs/designs/*.md)
- Current design phase (if /systems-design or /systems-design-review mode is active)
- Quick reference to available design mechanisms

Fires on: provider:request (ephemeral, not stored in history)
Priority: 5 (after status-context at 0, before todo-reminder at 10)
"""

__amplifier_module_type__ = "hook"

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> None:
    """Mount the design-context hook.

    Config keys:
        design_docs_glob: str  — glob pattern for design docs (default: "docs/designs/*.md")
        priority: int          — hook priority (default: 5)
    """
    from amplifier_core import HookResult

    config = config or {}
    design_docs_glob = config.get("design_docs_glob", "docs/designs/*.md")
    priority = config.get("priority", 5)

    # Resolve working directory from coordinator capability
    working_dir_str = coordinator.get_capability("session.working_dir")
    working_dir = Path(working_dir_str) if working_dir_str else Path(".")

    async def on_provider_request(event: str, data: dict[str, Any]) -> HookResult:
        """Inject design state context before each LLM call."""
        try:
            sections: list[str] = []

            # --- Section 1: Existing design documents ---
            design_docs = _scan_design_docs(working_dir, design_docs_glob)
            if design_docs:
                lines = [f"Design documents in this project ({len(design_docs)}):"]
                for doc in design_docs:
                    lines.append(f"  - {doc['relative_path']} ({doc['modified']})")
                sections.append("\n".join(lines))
            else:
                sections.append(
                    "No design documents found. "
                    f"Design docs are expected at {design_docs_glob}."
                )

            # --- Section 2: Active design mode (if any) ---
            session_state = getattr(coordinator, "session_state", {}) or {}
            active_mode = session_state.get("active_mode")
            if active_mode and active_mode in ("systems-design", "systems-design-review"):
                sections.append(f"Active design mode: /{active_mode}")

            # Assemble the injection
            content = "\n\n".join(sections)

            return HookResult(
                action="inject_context",
                context_injection=(
                    '<system-reminder source="hooks-design-context">\n'
                    f"{content}\n"
                    "\nProcess this silently. Do not mention design state to the user "
                    "unless directly relevant to their question.\n"
                    "</system-reminder>"
                ),
                context_injection_role="user",
                ephemeral=True,
                suppress_output=True,
            )
        except Exception as e:
            logger.error(f"hooks-design-context failed: {e}", exc_info=True)
            return HookResult(action="continue")

    coordinator.hooks.register(
        event="provider:request",
        handler=on_provider_request,
        priority=priority,
        name="hooks-design-context",
    )

    logger.info(
        "hooks-design-context mounted: scanning %s in %s",
        design_docs_glob,
        working_dir,
    )


def _scan_design_docs(working_dir: Path, glob_pattern: str) -> list[dict[str, str]]:
    """Scan for design documents matching the glob pattern.

    Returns a list of dicts with 'relative_path' and 'modified' keys,
    sorted by modification time (most recent first). Capped at 20 entries
    to avoid context bloat.
    """
    results: list[dict[str, Any]] = []
    try:
        for path in working_dir.glob(glob_pattern):
            if not path.is_file():
                continue
            stat = path.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            results.append(
                {
                    "relative_path": str(path.relative_to(working_dir)),
                    "modified": mtime.strftime("%Y-%m-%d"),
                    "mtime": stat.st_mtime,
                }
            )
    except (OSError, ValueError) as e:
        logger.warning("Failed to scan design docs: %s", e)
        return []

    # Sort by modification time, most recent first
    results.sort(key=lambda d: d["mtime"], reverse=True)

    # Cap at 20 entries and strip the sort key
    return [
        {"relative_path": d["relative_path"], "modified": d["modified"]}
        for d in results[:20]
    ]
