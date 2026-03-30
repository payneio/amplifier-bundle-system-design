# Tools: LLM-Decided Agent Capabilities

## What It Is

A tool is a capability the LLM can choose to invoke during its execution loop.
Tools follow a structural typing protocol -- any Python class with the right shape
(name, description, input_schema, execute) satisfies the `Tool` protocol. The LLM
sees the tool's name, description, and JSON schema, then decides when to call it.

## How It Works

### The Tool Protocol

```python
class Tool(Protocol):
    @property
    def name(self) -> str: ...           # Snake_case, unique

    @property
    def description(self) -> str: ...     # Rich text the LLM reads

    @property
    def input_schema(self) -> dict: ...   # JSON Schema for parameters

    async def execute(self, input: dict) -> ToolResult: ...
```

The `description` is the single most important field -- it's the LLM's only guide
for when and how to use the tool.

### Tool Dispatch Flow

1. Orchestrator collects all mounted tools from coordinator
2. Builds `ToolSpec` objects (name + description + schema) for each
3. Sends as `ChatRequest.tools` to the LLM
4. LLM returns `ToolCall`s when it decides to use a tool
5. Hooks fire `tool:pre` (can block/modify)
6. `tool.execute(arguments)` runs
7. Hooks fire `tool:post`
8. Result added to context for next LLM turn
9. Loop continues until LLM stops calling tools

### Module Loading

Tools are loaded via a `mount()` function that registers them on the coordinator:

```python
async def mount(coordinator, config) -> Tool:
    tool = MyTool(config)
    await coordinator.mount("tools", tool, name=tool.name)
    return tool
```

Discovery uses entry points (`pyproject.toml`), direct imports, or source URIs.
Supports polyglot transports: Python, WASM, gRPC, Rust sidecar.

### Multi-Tool Modules

A single module can register multiple tools. The filesystem module registers three:
`read_file`, `write_file`, `edit_file` -- all sharing config and coordinator access.

### Tools Calling LLMs

Tools can internally spawn child sessions. The `delegate` tool is the canonical
example: it calls `coordinator.get_capability("session.spawn")` to create an
entire child AmplifierSession with its own orchestrator, tools, and LLM calls.

### Bundle Composition

```yaml
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
```

### Key Implementation Files

- `amplifier-core/python/amplifier_core/interfaces.py:131-163` -- Tool protocol
- `amplifier-core/python/amplifier_core/models.py:37-100` -- ToolResult
- `amplifier-module-tool-bash/__init__.py` -- Reference implementation
- `amplifier-module-tool-filesystem/` -- Multi-tool module example
- `amplifier-foundation/modules/tool-delegate/` -- Tool that spawns agents

## Relevance to System Design Bundle

Custom tools could provide structured design capabilities:

- **Design model tool**: A tool that maintains a structured system model (goals,
  constraints, actors, interfaces, dependencies) that the LLM builds incrementally
  during design exploration. Unlike a context file, a tool can validate, transform,
  and persist structured data.

- **Tradeoff analysis tool**: A tool that takes design options and evaluation
  criteria, then produces a structured comparison matrix. The tool enforces the
  analysis framework (latency, complexity, reliability, cost, security, etc.)
  rather than relying on the LLM to remember the framework.

- **Constraint tracker**: A tool that maintains an explicit set of design
  constraints and checks proposed changes against them. Could flag when a design
  decision violates a previously established constraint.

- **Architecture diagram tool**: A tool that generates visual representations
  (dot-viz, mermaid) from the structured system model, giving the LLM a way to
  produce concrete artifacts during design.

However, tools are the heaviest mechanism -- each requires a Python module, entry
point, protocol compliance, and maintenance. For our initial experiments, skills
and context files may deliver faster value. Tools should be reserved for
capabilities that genuinely need structured data manipulation or external system
interaction.

Key question: Which design capabilities need the structure and validation that
tools provide vs. which can be accomplished through prompt engineering (skills/
context)?
