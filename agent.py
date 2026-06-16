#!/usr/bin/env python3
"""
ON24 SDR Pre-Call Brief Agent
Generates research-grounded pre-call briefs for ON24 sales development representatives.
"""

import os
import sys
import argparse
from datetime import date

import anthropic
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

SYSTEM_PROMPT = f"""You are an AI sales-research agent for ON24 SDRs. Your job is to take a Contact Name and Account Name and produce a complete pre-call brief that an ON24 SDR can read in 90 seconds and use to make a confident first call or send a personalised email.

Every output must be grounded in evidence retrieved during research. Never invent. If a fact cannot be sourced, say so explicitly.

Tone: professional, conversational, marketing-leader-fluent. No em dashes anywhere in your output. Do not narrate your research process.

ON24 sells digital engagement and demand-gen solutions to marketing leaders. Frame everything through that lens - webinars, demand gen, lead-to-revenue attribution, audience engagement, content programmes, account-based marketing.

Today's date is {date.today().strftime("%B %d, %Y")}.

When given a contact and account, run multiple targeted web searches:
- The contact's LinkedIn profile, role, tenure, and any public content or interviews
- The company's marketing strategy, recent news, press releases, and executive moves
- Whether the company runs virtual events, webinars, or content programmes
- Job postings in their marketing org (signals intent and priorities)
- Competitor context or industry pressures relevant to demand generation

Then produce a brief using exactly this format. Do not add sections or remove sections.

---
PRE-CALL BRIEF: [Contact Name] | [Account Name]
[Today's date]

CONTACT SNAPSHOT
Role: [current title and department]
Tenure: [time in current role and at company if known, or "not confirmed"]
Background: [2-3 sentence professional bio grounded in sourced facts]
LinkedIn: [URL if found, otherwise "not found"]

COMPANY SNAPSHOT
What they do: [one clear sentence describing the business]
Size: [headcount and/or revenue if known, otherwise "not confirmed"]
Marketing org: [what is known about their marketing team structure, headcount, or budget signals]

STRATEGIC CONTEXT
Priorities:
- [sourced priority 1]
- [sourced priority 2]
- [sourced priority 3 if found]

Recent signals:
- [relevant news item or public statement with approximate date]
- [second item if found]

ON24 ANGLE
Why ON24 fits: [specific, evidence-based reason this account is a strong fit - tie to their known priorities]
Use cases to explore:
- [ON24 use case 1 relevant to their situation]
- [ON24 use case 2]
- [ON24 use case 3 if applicable]
Timing signal: [any trigger event that makes outreach timely now - funding, new CMO, hiring surge, product launch, announced event programme, digital transformation initiative, etc. If none found, say "no strong trigger identified"]

PERSONALISED TALK TRACKS
Opening line (call): [one sentence personalised opener grounded in something specific from the research]
Opening line (email subject): [email subject line under 50 characters, specific not generic]
Discovery questions:
1. [question tied to a known priority]
2. [question about their current demand-gen or event approach]
3. [question that surfaces pain ON24 solves]
Anticipated objection: [the most likely pushback from this persona] -- Response: [one sentence reply]

SOURCES
[Numbered list of URLs or publication names used as evidence. If a claim is unverified, note it.]
---

If you cannot find meaningful information on either the contact or the account after searching, say so clearly in the relevant section. Never pad the brief with generic marketing statements that are not grounded in research."""


TOOLS = [
    {"type": "web_search_20260209", "name": "web_search"}
]


def run_agent(contact_name: str, account_name: str, verbose: bool = False) -> str:
    """Run the research agent and return the completed pre-call brief."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    messages = [
        {
            "role": "user",
            "content": (
                f"Contact Name: {contact_name}\n"
                f"Account Name: {account_name}\n\n"
                "Research this contact and account thoroughly, then produce the pre-call brief."
            ),
        }
    ]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
            betas=["web-search-20260209"],
        )

        if verbose:
            for block in response.content:
                if getattr(block, "type", None) == "tool_use":
                    query = getattr(block, "input", {}).get("query", "")
                    if query:
                        print(f"  [search] {query}", file=sys.stderr)

        if response.stop_reason == "end_turn":
            for block in response.content:
                if getattr(block, "type", None) == "text":
                    return block.text
            return "No brief generated."

        if response.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": response.content})
            continue

        break

    return "Agent stopped unexpectedly."


def interactive_mode():
    """Run the agent as an interactive chat-style session."""
    print("ON24 SDR Pre-Call Brief Agent")
    print("Type a contact and account to research, or 'quit' to exit.\n")

    while True:
        try:
            contact = input("Contact name: ").strip()
            if contact.lower() in ("quit", "exit", "q"):
                break
            if not contact:
                continue

            account = input("Account name: ").strip()
            if account.lower() in ("quit", "exit", "q"):
                break
            if not account:
                continue

            print(f"\nResearching {contact} at {account}...\n")
            brief = run_agent(contact, account, verbose=True)
            print("\n" + brief + "\n")
            print("-" * 60 + "\n")

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break


def main():
    parser = argparse.ArgumentParser(
        description="ON24 SDR Pre-Call Brief Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Run with no arguments for interactive mode.\n\n"
            "Examples:\n"
            '  python agent.py\n'
            '  python agent.py "Sarah Chen" "HubSpot"\n'
            '  python agent.py "Marcus Webb" "Salesforce" --verbose\n'
            '  python agent.py "Priya Sharma" "Zendesk" --output brief.txt'
        ),
    )
    parser.add_argument("contact", nargs="?", help="Full name of the contact")
    parser.add_argument("account", nargs="?", help="Name of the account/company")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show search queries as they run"
    )
    parser.add_argument(
        "--output", "-o", metavar="FILE", help="Save the brief to a file instead of printing"
    )

    args = parser.parse_args()

    if not ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    if not args.contact and not args.account:
        interactive_mode()
        return

    if not args.contact or not args.account:
        parser.error("Provide both a contact name and account name, or neither for interactive mode.")

    if args.verbose:
        print(f"Researching {args.contact} at {args.account}...\n", file=sys.stderr)

    brief = run_agent(args.contact, args.account, verbose=args.verbose)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(brief + "\n")
        print(f"Brief saved to {args.output}", file=sys.stderr)
    else:
        print(brief)


if __name__ == "__main__":
    main()
