# Agent instructions

This repository holds BrAIan's videos as HyperFrames projects, one folder per video, plus `logo/` with the mascot master. Read `README.md` for the layout.

- Before making, editing or rendering a video, load the `hyperframes` skill (in `.agents/skills`); each video folder's own `AGENTS.md` lists the rest.
- The skills in `.agents/skills` are vendored from upstream (see each `PROVENANCE.md`): update them from upstream together, never edit them in place.
- Commit sources and the delivery renders (MP4, WebM). Never commit ProRes `.mov` files, `.hyperframes/`, `.thumbnails/` or `.waveform-cache/`.
- After changing a video, render it again and update its README if the files or commands changed.
