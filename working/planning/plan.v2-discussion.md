Ok, so the following is through the lens of "the parts in isolation, apart from how they'll be tied together into solutions/systems".  Since I suspect your revision through the other lens will cause these to change further, this is more commentary on the choice of mechanism vs a more comprehensive thinking about how they interact with each other or get invoked.
 
ChkPt1: where do you expect those context files to be leveraged? Are they injected via context.include and therefore get force loaded into the main instruction load (seems that is what it says), or online one/some of them be included that way and others more "soft mentioned"? Also, why at this level and how much do you expect this will increase our basic "hi" (no history, etc.) payload token cost?  At this level, it's being added to every main session llm request (and any subsession that inherits instead of having their own instruction), even for work that has nothing to do w/ system design, etc.  We're generally moving away from this approach and trying to be lighter here, so this may be a better "if in the end, we still need something here" vs a starting point?

ChkPt2: lgtm
 
ChkPt3: do we want the command to own the /system-design space or would it be better to be something like /system-design and /system-design-review to be more explicit about the kind of design we're invoking for and to avoid users confusing with thinking they are getting a UI/UX design experience?
 
ChkPt4: lgtm
 
ChkPt5: lgtm
 
ChkPt6: I'd recommend use of tools here, this may be better as agents instead of skills for that reason.
 
ChkPt7: I like this, but maybe time-box - if you get the rest done by Thurs, this might be a good one to wrap your week w/ along with any other refinements from discoveries you make along the way?
 
Overall - thoughts on leveraging some of the value we're discovering from use of the dot-graph bundle (even adding it as a dependency in your behavior bundle) for use in some of these?  For example, I could see leveraging it in the modes, recipes, and some of the others? In addition to the obvious use of communicating w/ the user (like how the brainstorm mode uses the mock-up visuals to help communicate and get feedback from users), we also find these to be very useful for identifying issues/bugs when the models/agents are forced to represent code/designs/etc. in this format, or for comparing what was built (build the dot representation from code only, not docs/spec/etc.) w/ what was intended/planned (original planning dot files), etc.
 
Also, Ryan's "Crusty Old Engineer" skill has been working quite well for me in this area as well, providing some pretty good gap-filling advice that other agents/skills seem to miss - so while we don't need to bring that in necessarily, it may be good to see how well it aligns to your work here and if it would make sense to mine/scrape it into your work such that we don't have a reason we'd want to also use it - or if it's different enough or would stretch your work beyond it's intent, then we can use it separately for those of us who want to.

---

We often build something with amplifier, but it ends up just being source code and tests usually. I'm wondering if we couldn't add the idea of "deploy targets"?
