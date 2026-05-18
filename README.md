# Prague School Capacity Research

Estimate the chance that a child born in **2021** or **2024** gets into each elementary school in Prague districts **3, 7, 8, 9, 10, 14**.

## Where to look

| Need | File |
|---|---|
| Project goals, principles, directory layout, subagent contract | [`CLAUDE.md`](./CLAUDE.md) |
| **How to re-run this analysis in 6–36 months** | [`RERUN.md`](./RERUN.md) |
| Current state of each work package | [`progress/master-plan.md`](./progress/master-plan.md) |
| Catalogue of every data source (with tier + dead-end log) | [`memory/sources.md`](./memory/sources.md) |
| Czech terms cheat-sheet | [`memory/glossary.md`](./memory/glossary.md) |
| Final deliverables (plots, the answer) | [`findings/`](./findings/) |

## Running this project

It is operated by a Claude Code orchestrator agent. Two operating modes:

- **Fresh build** — start in this directory, read `CLAUDE.md`, dispatch work packages WP-01 through WP-05 per `progress/master-plan.md`.
- **Periodic refresh** — read `RERUN.md`. Each section is a self-contained recipe for one fruitful data-extraction step. Re-run all sections in order; outputs land in `memory/raw/` and `memory/aggregated/`.

The refresh path is deliberately narrower than the fresh-build path: it skips every dead-end and exploratory step the original run did.
