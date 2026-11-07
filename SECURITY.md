# Security Policy

OpenYantra keeps personal memory on your own machine. Security reports are taken seriously.

## Supported versions

| Version | Supported |
| --- | --- |
| 6.x (latest) | Yes |
| Earlier than 6.0 | No |

## Reporting a vulnerability

**Do not open a public issue for a security problem.**

Use GitHub's private reporting: go to the **Security** tab of this repository and choose **Report a vulnerability**
(https://github.com/revanthlevaka/OpenYantra/security/advisories/new).
If you cannot use that, email revanth@revanthlevaka.com with "OpenYantra security" in the subject.

Please include:

- what you found and which file or command it affects
- steps to reproduce, or a short proof of concept
- the version (`yantra --version`) and your operating system

## What to expect

- Acknowledgement within 3 days.
- A first assessment within 7 days.
- A fix or a clear plan within 30 days for confirmed issues, and credit in the changelog if you want it.

## In scope

- The Chitrapat file handling, the write queue and the audit ledger (Agrasandhani)
- Raksha, the security engine (injection and sanitiser bypasses)
- The web dashboard, HUD, passkey login and MCP server
- Adapters and installers (`install.sh`, `install.ps1`)

## Out of scope

- Attacks that need prior full access to your machine or your Chitrapat file
- Findings in third-party packages with no OpenYantra-specific impact (report those upstream)
- Denial of service against a local-only service on your own machine

## Automated checks on this repository

CodeQL, dependency review, secret scanning (Gitleaks), `pip-audit` and Dependabot run on every pull request and weekly.
