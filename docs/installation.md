# Installation

These are release-candidate instructions. Record actual client version, account
plan/workspace policy, installation result and skill activation before claiming
support. No CoverCount sign-in is required for this anonymous endpoint; the host
client can still require its own account or administrator access.

## OpenAI: ChatGPT and Codex

Use `covercount-explore-openai-0.2.0.zip`. It contains one `covercount-explore/`
plugin directory with portable root `plugin.json`, `mcp.json`, all three skills
and assets. A `.codex-plugin/plugin.json` / `.mcp.json` compatibility pair is also
included. All formats refer to the same anonymous endpoint.

For local acceptance, extract the plugin and add that directory through a supported
local plugin/marketplace installation flow. Enable it in a fresh conversation and
run the [acceptance cases](evaluations.md). Bare MCP connection testing does not
establish installation or activation of the bundled skills.

For submission, use packaged-skill upload alongside the remote MCP connection;
see [submission](submission.md). This release does not expose an MCP skill-resource
import extension or include a fabricated registered app ID.

Current documentation: [OpenAI packaging](https://developers.openai.com/plugins/build/plugins),
[skill delivery](https://developers.openai.com/plugins/build/skills), and
[complete-plugin testing](https://developers.openai.com/plugins/deploy/connect-chatgpt).

## Claude Code

Use `covercount-explore-claude-0.2.0.zip` or this checkout. Extract the archive and
point Claude Code at its `covercount-explore` directory:

```powershell
claude plugin validate D:\path\to\covercount-explore --strict
claude --plugin-dir D:\path\to\covercount-explore
```

The Claude package contains `.claude-plugin/plugin.json`, `.mcp.json`, the same
three skills and assets. In a fresh session, verify the connection and naturally
phrased requests. Explicit skill invocation alone does not establish automatic
activation. See the [Claude manifest reference](https://code.claude.com/docs/en/plugins-reference).

## Claude chat / Cowork

Use the Claude package in an available plugin upload or organization distribution
flow. Check the exact client surface and account/workspace prerequisites first.
Organization distribution is documented separately from Claude Code's local loading:
[Claude organization plugin distribution](https://claude.com/docs/plugins/org-sync).
Validate the installed skills and MCP connection together in the actual chat/Cowork
surface. A Claude Code manifest check is not evidence of Claude chat support.

## Connection and updates

The only remote dependency is `https://mcp.covercount.io/explore/mcp`, named
`covercount-explore`. No token, API key, OAuth setup, environment variables or
startup command belong in this package. A connection without bundled skills is
tool-only acceptance.

When sources change, update all three manifest versions and affected skill versions,
rebuild, reinstall/refresh through the target client and start a fresh conversation.
Server deployment and client-package refresh are separate actions.
