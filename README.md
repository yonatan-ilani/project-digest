# project-digest

A living project dashboard for devs and PMs, kept current by a Claude Code
skill instead of a cron job.

- **`/digest`**: Claude reads your tracker, chat, docs and git, diffs against
  the last run, asks you only about the judgment calls, then rebuilds the page and commits.
- **The page**: one static `index.html` with the data inlined. No backend and no
  network calls. It works from `file://`, GitHub Pages, S3, or an internal static host.

**Live demo** (fake data): https://nehoil.github.io/project-digest/

```
 sources.json ──▶ /digest (Claude, supervised) ──▶ data.json ──▶ build.py ──▶ index.html
 tracker·chat      read ─ diff ─ assess ─ interview                            (static page)
 docs·git          ✗ failed source → marked stale, never blocks                 ▲ PMs watch
```

## Use it for your project

1. Use this repo as a template. Make it **private** if your data is internal.
2. Edit `sources.json` so it lists your tracker, channel, repos and docs. `via`
   names the tool: an MCP (Linear, Jira, GitHub, Slack, Drive, Notion…), `gh`, `git`, or `file`.
3. Set `digestCount` to `0` in `data.json` and run `/digest` in Claude Code
   inside the repo. The first run interviews you for phases and teams and
   replaces the Acme sample.
4. Optionally set `"publish"` in `sources.json` (for example `"git push"` with
   Pages enabled) so each digest redeploys the page.

`/digest quick` refreshes the source-backed data only and skips the interview.

## Files

| file | role |
|---|---|
| `template.html` | the view. Edit it on purpose; digests don't touch it. |
| `data.json` | the only file a digest writes |
| `build.py` | inlines `data.json` into `template.html`, producing `index.html` |
| `sources.json` | what to pull, plus an optional `publish` command |
| `.claude/skills/digest/SKILL.md` | the digest procedure |

## Entities

- **Auto** entities (ticket status, commits, stats) are re-derived from sources
  and only change when their meaning changes. Prior wording is kept.
- **Judgment** entities (roadmap, blockers, health, agenda, stakeholders) carry
  over between runs and change only through the interview. They're flagged as
  stale after 7 days without confirmation.

## data.json schema

```jsonc
{
  "meta": {
    "project": "Name", "lastDigestAt": "ISO8601", "startDate": "ISO8601", "digestCount": 1,
    "currentMilestoneId": "ms-…",
    "issueUrl": "https://linear.app/acme/issue/{id}",   // {id} ← ticketId; omit for plain text
    "teams": [["FE","Frontend"],["BE","Backend"]],        // issue swimlanes
    "health": { "status": "on-track|blocked", "why": "one line" }
  },
  "roadmap": [ { "id", "name", "status": "done|current|upcoming", "progress": 0-100,
                 "targetDate", "summary", "blockerIds": [],
                 "issues": [ { "id", "title", "status": "done|in-progress|todo|blocked",
                               "team", "ticketId": null } ] } ],   // null ticketId = untracked gap
  "agenda":       { "targetDate", "daysRemaining", "focus": [ { "priority", "owner", "ticketId", "title", "why", "tag" } ] },
  "blockers":     [ { "id", "title", "detail", "owner", "phaseId", "ticketId", "since", "staleSince" } ],
  "sources":      [ { "id", "label", "type": "live|context", "lastSync", "ok", "note" } ],
  "stakeholders": [ { "id", "name", "role", "owns", "trackerUser" } ],
  "stats":        { "commits", "linesAdded", "prs", "repos": [] },
  "specLinks":    [ { "label", "url" } ],
  "timeline":     [ { "date", "type", "entityId", "summary" } ],
  "delta":        [ /* this run's events only */ ]
}
```

Timeline event types: `ticket_closed`, `ticket_opened`, `blocker_added`,
`blocker_resolved`, `milestone_passed`, `workstream_advanced`, `spec_changed`,
`stakeholder_changed`.

## Privacy

A public Pages site exposes everything in `data.json`. Real project data belongs in
a private repo on an access-controlled host.
