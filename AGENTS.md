# CoverCount Explore client

This is the canonical Explore client repository. Keep maintained skills under
`skills/`, and plugin manifests, assets and public documentation in this repository.
Do not put Explore client sources in `covercount_mcp_public` or `resources`.

The workspace's MCP server implementation lives in `../api`; planning and status
live in `../resources`. Read `../resources/spec-public-explore-mcp.md` and
`../resources/implementation-status.md` before changing contracts or guidance.

The anonymous Explore endpoint is `/explore/mcp`; `/mcp` is the
authenticated staff endpoint. Explore skills must not depend on staff tools.
Use a distinct Explore plugin identity and preserve coexistence with the staff client.

Reservations is the default mode, followed by Events and Places. Preserve local
dates/timezones, explicit incomplete/unknown outcomes, and booking handoff language.
Do not collect guest contact details or consent, create bookings, or claim that
visiting a handoff URL confirms a booking.

Validate manifests, skill references, archive contents and endpoint selection when
packaging is implemented. Generated archives go to `../resources/dist`, never
maintained source copies. Local validation, deployment, client installation,
submission, approval and publication are separate outcomes.
