# Release and submission materials

Release candidate: **covercount-explore 1.0.0**. Server contract: **0.4.0** or
compatible later. This document prepares submission; it does not record publication.

## Listing copy

**Name:** CoverCount Explore

**Short description:** Find places, events & tables

**Description:** Discover public places, events and reservation openings by location
and visit details. Check a selected opening's card requirement, then finish booking
on CoverCount. Search does not book or hold anything. No CoverCount account is needed
for discovery. Availability and payment requirements are rechecked on the website.

**Publisher:** CoverCount. **Website:** https://explore.covercount.io/

**Documentation:** https://www.covercount.io/learn/connected-apps/covercount-explore

**Repository:** https://github.com/chriswill/CoverCount_Public_Mcp

**Support:** https://support.cloudscope.io/

**Privacy:** https://www.covercount.io/privacy

**Terms:** https://www.covercount.io/terms-of-service

Starter prompts are in the README and OpenAI metadata. Existing CoverCount icons
and logos are included in `assets/`; they are brand assets, not a trademark grant.
No screenshots or invented review credentials are supplied.

## Connection and tool review

Remote HTTPS endpoint: `https://mcp.covercount.io/explore/mcp`.
Authentication: anonymous. No CoverCount account, OAuth scopes or reviewer login.

| Tool | User purpose | Hint rationale |
| --- | --- | --- |
| `search_available_reservations` | Find public openings for a date/party | Reads public inventory; no booking or hold |
| `get_reservation_opening` | Recheck one opening and its card requirement | Reads eligibility, inventory and payment rules; no provider action |
| `get_public_venue` | Describe one selected public venue | Reads public description, links, contact details, photos and local hours; no booking or inventory assertion |
| `search_public_events` | Find public event series in a supported window | Reads dates, restrictions and starting prices; no registration |
| `search_places` | Find public venues | Reads listings independently of inventory |

All tools have readOnlyHint=true, destructiveHint=false, idempotentHint=true and
openWorldHint=true. Idempotent describes absence of consequential mutations; live
results can change. Open-world is conservative because locality resolution can call
external geocoding. Public cache/budget housekeeping creates no guest bookings.

## OpenAI release procedure

Upload **`covercount-explore-openai-1.0.0.zip`** as the complete plugin in the OpenAI
plugin portal. The initial upload includes all three skills and the production MCP
connection. Choose the verified developer identity, review Metadata & Skills,
then connect the anonymous server under MCPs, complete domain verification and
review the tool scan. Do not use the skills-only archive for this submission.
See [OpenAI's ZIP submission guide](https://developers.openai.com/plugins/deploy/submission).

The package supplies a square emblem, a subtitle within the 30-character limit,
and all four listing URLs. Before final review, complete five positive and three
negative test cases, an accessible video walkthrough and release notes in the
portal or supported package review metadata. No reviewer login is required for
this anonymous connector. This package does not claim those review steps are done.

Before authorized submission:

- Verify hosted anonymous initialization, the five-tool catalog and valid searches.
- Confirm required server configuration and SQL deployment with the server owner.
- Check policy/support URLs, listing copy and generated inventory hashes.
- Run [acceptance cases](evaluations.md) in ChatGPT and Codex, recording actual surfaces.
- Verify not-booked wording, card outcomes and working website links.
- Upload the complete OpenAI plugin ZIP and review the draft.
- Track submission, approval and publication separately; a local build or tool scan
  is not a published combined plugin.

## Claude release procedure

Validate the Claude package, then install it through the intended local or hosted
route. Run acceptance separately in Claude Code and Claude chat/Cowork. Use the
same listing copy, policy links and five-tool boundary for the chosen directory or
organization submission. This repository has no published remote URL assigned yet;
do not invent one or register a marketplace as part of a build.

Publication and organization-wide distribution require the owner's release
instruction. Local build/validation do not submit, install globally or publish.
