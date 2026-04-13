# Systems design bundle

Currently, much of our system design intent is in content documents that get loaded into context (like PHILOSOPHY.md, or AGENTS.md). Superpowers /brainstorm does a good job of interacting with a user to make _some_ decisions. Neither of these methods replace system design expertise.

When the systems design bundle is used, it provides a structured approach to understanding, evaluating, and improving system designs.

- top-level systems design content (a set of principles, patterns, and practices we prioritize to follow in our systems design). This wouldn't be amplifier's existing docs, something more generic and comprehensive as a backbone about system design

- If we can answer "what kind of system is this", we could also create additional content about specific system types (e.g. web service, web app, peer-to-peer system, etc.) that would be loaded in when relevant to provide more specific guidance and best practices for those types of systems.

The bundle should help you:

- Get a full systems understanding of an existing codebase.
- Get a full systems understanding of any part of a system.
- Evaluate a systems design proposal.
  - Review a proposed design (against the actual codebase) for: 
    - design integrity
    - pros/cons
    - developer experience (DX)
    - implementation viability
    - simplicity
    - tooling consistency

Bonus capabilities to consider:

- Constraint management: Design is all about constraints (aka tradeoffs). This bundle should also include some tools for identifying, evaluating, and making tradeoffs in a design. This is one of the most important parts of design, and often the hardest to get right. It also has a lot of nuance and complexity to it, so having some tools to help with this would be really valuable.
- Design modeling: It is expensive to build out full implementations before finding design flaws. We should have better tools for modelling and simulating designs before building them out. dot-viz is a good start, but is there a more comprehensive model we can create that can be exercised? For example, can we encode an "amplifier bundle model" that we could compare proposed designs against, and simulate how they would work with different agents, bundles, contexts, etc.? Related things would be "web-app model" or "web-wasm model" or "web service model" or "peer-to-peer model". If there's a way to express these things, then proposed work could be tested against them to find flaws before a full implementation.
