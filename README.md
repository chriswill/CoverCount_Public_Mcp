# CoverCount Explore

Find public reservation openings, events and places, then finish booking on
CoverCount. Discovery needs no CoverCount account.

**Your reservation is not booked or held by chat.** Follow **Finish booking on
CoverCount** and complete the website flow for confirmation. The website collects
guest details and consent and rechecks availability and card requirements.

Try:

- “Find a tasting reservation for four in Napa tomorrow afternoon.”
- “What public events are in Paso Robles this weekend?”
- “Help me discover wineries near Sonoma.”
- “What is this venue like? Can I see its menu and hours?”

The three skills distinguish a new reservation search, event discovery, and places
without an availability requirement. They do not look up existing bookings, buy
tickets, manage a venue, send messages, or collect contact/payment details in chat.
An unknown card requirement never means no card is required. Searches do not start
automatic monitoring or schedules.

For a selected venue, the public profile provides its description, menu/website,
address, public contact details, photos and local hours when supplied. Missing
profile fields do not establish that the venue lacks those details.

## Install and review

Version **1.0.1**, release candidate. Requires the public server contract implemented
in **0.4.0** or a compatible later version at
`https://mcp.covercount.io/explore/mcp`. Client installation, skill activation and
hosted acceptance are recorded separately; local package validation does not prove them.

- [Installation](docs/installation.md) covers OpenAI and Claude package layouts.
- [Submission materials](docs/submission.md) contain listing copy and release checks.
- [Acceptance cases](docs/evaluations.md) cover positive, negative and edge requests.

The plugin/MCP connection name is `covercount-explore`. The staff CoverCount plugin
is a separate product with its own connection. Do not change this connection to
the staff endpoint. Verify coexistence in the intended client before release.

## Privacy and support

Search sends the criteria you supply, such as locality, date and party size, to
CoverCount. Typed localities may use Google's geocoding service; supplied coordinates
and cached place results follow the server's discovery behavior. Do not put guest
contact or payment details into search criteria. The website handles booking data
if you choose to continue there. The package contains instructions and a remote
connection, with no credentials or executable booking code.

[Explore](https://explore.covercount.io/) ·
[Support](https://support.cloudscope.io/) ·
[Privacy](https://www.covercount.io/privacy) ·
[Terms](https://www.covercount.io/terms-of-service)

## Source and license

This repository is the canonical Explore client source. Maintain skills only in
`skills/`. The workspace builder reads this checkout and generates packages in
`../resources/dist`; it does not synchronize maintained copies elsewhere.

For development, install `requirements-dev.txt` in a virtual environment, run
`python scripts/validate_plugin.py` and `python -m unittest discover -s tests -v`,
then run `python ../resources/scripts/build-covercount-explore-plugin.py` from this
checkout in the full workspace. The builder checks tool references against the
server catalog and emits separate OpenAI, Claude and skill-upload archives plus
a SHA-256 inventory. It never installs or publishes anything.

Plugin manifests, skills and documentation use the Apache License, Version 2.0;
see [LICENSE.txt](LICENSE.txt). That license does not grant rights to the CoverCount
name, logos or other brand assets in `assets/` (Section 6).

Guest documentation: [CoverCount Explore setup and usage](https://www.covercount.io/learn/connected-apps/covercount-explore).

Source repository: [CoverCount Explore on GitHub](https://github.com/chriswill/CoverCount_Public_Mcp).
