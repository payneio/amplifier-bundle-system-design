We are exploring improving the systems design capabilities of an agentic system. For background, read https://payne.io/posts/intelligent-design and ./agentic-system-design.md.

The system we will be working to improve is https://github.com/microsoft/amplifier. Amplifier is an agentic ecosystem where the agent loop is enhanced with additional capabilities using "bundles". We will be creating a new "system-design-intelligence" bundle.

Some initial thoughts on how we might start breaking up this work are included in ./investigation.md.

Right now, I'd like to continue refining how we will experiment in this area with concrete value delivered daily as we dig in deeper.

To help with that, I think you should also investigate the following amplifier systems:

- Bundle creation and composition
- Specific ways Amplifier uses currently for extending the capabilities of agents, including:
  - tools
  - hooks
  - skills (lots of recent work in making this more capable recently)
  - recipes
  - content (markdown files fed into the LLM context)
  - agents
  - modes
- The superpowers bundle that is included in https://github.com/microsoft/foundation (the /brainstorm mode is relevant)

As we start our investigation, I think it would be good make a small markdown document in ./docs/amplifier-facilities/*.md for each method of extending Amplifier capabilities that describes what it is and how it might relate to our system design bundle. Think of these a mini-research docs that are looking up what capabilities actually exist. You'll want to look at actual code, not just documentation. To help you with that, I created a directory ./related-projects/ that you can clone other git repositories into as you find them. Amplifier has hundreds of repositories, so it will be good to clone each thing you want to look into locally like this.


