# Fusion Skills

Claude skills for working with Autodesk Fusion through the Fusion MCP server.

## Skills

| Folder | What it does |
|---|---|
| [`fusion-addin-creator`](fusion-addin-creator/) | Scaffolds a new Fusion add-in from a standard template. |
| [`fusion-design-practices`](fusion-design-practices/) | Design conventions for modeling, sketching, assemblies and scripting, plus scripts for building a product structure and mirroring components. |
| [`fusion-ui-setup`](fusion-ui-setup/) | Hides distracting UI panels at the start of a Fusion session, after asking permission. |
| [`fusion-wcs-orientation`](fusion-wcs-orientation/) | Detects whether a design is Z-up or Y-up and picks the matching sketch plane and extrude axis. |

Each folder is a self-contained skill: a `SKILL.md` with the instructions, and
for `fusion-design-practices` also `references/` and `scripts/`.

## Installing

**Claude Code:** copy the skill folders you want into `~/.claude/skills/`
(or into `.claude/skills/` inside a project).

```sh
git clone https://github.com/schneik80/fusion-skills.git
cp -R fusion-skills/fusion-design-practices ~/.claude/skills/
```

**Claude apps:** zip a skill folder and upload it under Settings > Capabilities > Skills.

## Notes

`fusion-addin-creator` copies from a local add-in template whose path is
hard-coded in its `SKILL.md`. Change that path to your own template before
using it.

## License

[MIT](LICENSE)
