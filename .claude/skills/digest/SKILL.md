---
name: digest
description: Refresh this repo's project dashboard. Reads every live source in sources.json (issue tracker, chat, docs, git), semantic-diffs against the previous data.json, runs a short interview for judgment calls, then rebuilds index.html and commits. Use when the user runs /digest in a project-digest repo. "/digest quick" = source-backed updates only, no interview.
---

# Digest — refresh the project dashboard

You are running a **digest**: a live, supervised refresh of the project dashboard
in this repo. The page makes zero network calls. *You* are the only thing that
touches sources, and you do it with the user watching.

**Mode:** `/digest quick` → steps 1–4 + 7 only (no interview). Otherwise all steps.

## Ground rules

- **Schema is frozen.** The schema is in `README.md`. Change entity *values* in
  `data.json`; never add/remove top-level keys or invent panels.
- **Two kinds of entities:**
  - **Auto** (source-backed: ticket status, commits, spec changes, stats):
    re-derive from sources, semantic-diff vs. the previous `data.json`, update
    only what *meaningfully* changed. Keep prior phrasing unless the meaning changed.
  - **Judgment** (roadmap shape, phase status/progress, blockers, stakeholders,
    health, agenda): carry forward from the previous `data.json`; evolve via the
    assessment (step 3b) and confirm in the interview (step 5). Never regenerate
    from scratch.
- **Stable ids.** Source-backed entities reuse upstream ids (ticket key, git SHA,
  message ts). Judgment entities keep their coined slug (`blk-…`, `sh-…`) across
  runs. When a gap gets ticketed, the slug stays and `ticketId` attaches.
- **Stale = 7 days.** A judgment entity whose `staleSince` is >7 days before
  `meta.lastDigestAt` gets re-asked in the interview.

## Steps

1. **Load state.** Read `data.json` and `sources.json`. Previous
   `meta.lastDigestAt` is the window start for chat and git.

2. **Read every `live` source** (skip `context` unless this is the first run).
   Each source names its tool in `via`: find the matching MCP with ToolSearch
   (Linear, Jira, GitHub, Slack, Google Drive, Notion…), or use `gh` / `git` /
   the filesystem. **A failed source never blocks**: set its `ok:false` with a
   `note` and keep going. Update each `data.json.sources` entry's `ok` + `lastSync`.

3. **Diff auto entities.** Set `delta = []`. Re-derive ticket statuses, commit
   counts (`stats`), and doc state. For each meaningful change, append a typed
   event to both `timeline` and `delta`. Event types: `ticket_closed`,
   `ticket_opened`, `blocker_added`, `blocker_resolved`, `milestone_passed`,
   `workstream_advanced`, `spec_changed`, `stakeholder_changed`.

3b. **Roadmap assessment.** Step back and look at the whole project:
   - Keep the phase set stable across runs (don't churn names). Set
     `meta.currentMilestoneId` to the phase the team is actually focused on.
   - Assign every open ticket to a phase and a team from `meta.teams`. Work with
     no ticket is a gap (`ticketId: null`). List it anyway.
   - Recompute each phase's real `progress` and `status`.
   - Rewrite `agenda.focus`: the 3–5 things that matter most today, each with
     an owner and a one-line why.

4. **Stamp.** Set `meta.lastDigestAt` to now and bump `meta.digestCount`.

5. **Lite interview** (skip in quick mode). Keep it short and don't walk the
   whole board. Use AskUserQuestion when it's available. Ask only about:
   - judgment items a diff touched ("#137 closed. Does that clear `blk-…`?"),
   - judgment items past the 7-day stale mark,
   - your roadmap assessment (current phase, anything you re-assigned),
   - one catch-all: "anything new? blockers, missing work, people?",
   - **always** one last question: "any new source I should pull from?" If the
     user names something fetchable, offer to add it to `sources.json`.
   For each surfaced item, offer: **Ticket it** (draft it in the tracker from
   `sources.json`, **confirm before creating**, then attach `ticketId`),
   **Keep local** (judgment entity, owner as plain text), or **Resolved**
   (for blockers, emit `blocker_resolved`). Update `meta.health`. Refresh
   `staleSince` on every item you touched.

6. **Confirm tracker writes.** Only the ones the user approved.

7. **Rebuild, commit, publish.**
   ```bash
   python3 build.py
   git add -A && git commit -q -m "digest $(date +%F): <one-line delta summary>"
   ```
   If `sources.json.publish` is set, run it (e.g. `git push`, which redeploys
   GitHub Pages, or an upload to an internal static host). Then tell the user
   what changed and which tickets you created.

## First run

If `meta.digestCount` is 0 or missing, this is a bootstrap. Read the `context`
sources too. Interview the user for the phase list, teams, and issue URL pattern.
Backfill `timeline` from closed tickets, `git log`, and milestone dates so the
page isn't empty. Replace all example data. Nothing from the Acme sample survives.
