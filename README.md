# ON24 SDR Pre-Call Brief Agent

An AI research agent that generates a complete, evidence-grounded pre-call brief for ON24 SDRs. Give it a contact name and account name and it returns a structured brief an SDR can read in 90 seconds and use immediately for a first call or personalised email.

Every fact in the output is sourced from live web research. The agent never invents information.

## What it produces

- Contact snapshot: role, tenure, bio, LinkedIn URL
- Company snapshot: what they do, size, marketing org signals
- Strategic context: sourced priorities and recent news
- ON24 angle: why this account fits, specific use cases, timing trigger
- Personalised talk tracks: opening lines, discovery questions, anticipated objection with response
- Sources list

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get API keys

**Anthropic API key** - https://console.anthropic.com

**Tavily API key** (free tier available) - https://app.tavily.com

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and add your keys
```

## Usage

```bash
python agent.py "Contact Name" "Account Name"
```

### Options

| Flag | Description |
|------|-------------|
| `--verbose` / `-v` | Print search queries to stderr as they run |
| `--output FILE` / `-o FILE` | Save the brief to a file |

### Examples

```bash
# Print brief to terminal
python agent.py "Sarah Chen" "HubSpot"

# Watch searches run, then save brief to file
python agent.py "Marcus Webb" "Salesforce" --verbose --output marcus_webb_brief.txt

# Pipe to clipboard (macOS)
python agent.py "Priya Sharma" "Zendesk" | pbcopy
```

## How it works

The agent uses Claude (claude-sonnet-4-6) with tool use. It runs multiple targeted web searches - contact LinkedIn, company news, marketing org signals, job postings, virtual event history - then synthesises everything into the brief format. If information cannot be sourced, it says so rather than guessing.

Typical runtime: 30-60 seconds depending on how much public information is available.

## Framing

Everything is framed through ON24's value proposition: digital engagement, webinars, demand generation, lead-to-revenue attribution, audience analytics, account-based marketing, and content programmes for marketing leaders.
