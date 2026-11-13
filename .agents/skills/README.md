# Skills

Every folder here is one skill: a `SKILL.md` with a `description` that says when to load it, depth in `references/`, scripts in `scripts/`. Claude Code reads them through the `.claude/skills` symlink; Codex scans this folder itself. They are third-party, updated from upstream, never edited in place.

| Skill | Owner | Load it for |
| --- | --- | --- |
| `hyperframes` | HeyGen (`heygen-com/hyperframes`, Apache-2.0; see its `PROVENANCE.md`) | Making, animating and rendering a video as HTML with HyperFrames, such as `intro/` |
| `hyperframes-cli` | HeyGen (`heygen-com/hyperframes`, Apache-2.0) | The `hyperframes` CLI: scaffold, preview, check frames, render |
| `hyperframes-registry` | HeyGen (`heygen-com/hyperframes`, Apache-2.0) | Ready-made HyperFrames blocks: titles, transitions, overlays, kinetic type |
| `media-use` | HeyGen (`heygen-com/hyperframes`, Apache-2.0) | Music, sound effects, voiceover and other media for a HyperFrames video, and mixing the audio |
