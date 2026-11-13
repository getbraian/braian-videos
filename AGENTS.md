# Agent instructions

This repository holds BrAIan's reusable video assets as HyperFrames projects, one folder each in `assets/` (with the mascot master in `assets/logo/` and music in `assets/audio/`), and the finished episodes in `final/`, one folder per recording in `raw/`. Read `README.md` for the layout.

- Before making, editing or rendering an asset, load the `hyperframes` skill (in `.agents/skills`); each asset folder's own `AGENTS.md` lists the rest.
- Every asset has a `<name>.preview.mp4` at the top of its folder (the 1080p master's copy). Refresh it whenever the asset is rendered again.
- Keep everything needed to make an asset again in its folder: compositions, media, and the experiments behind choices (for example `assets/intro/sound-sets/`).
- The skills in `.agents/skills` are vendored from upstream (see each `PROVENANCE.md`): update them from upstream together, never edit them in place.
- Commit sources, the preview and the delivery renders (MP4, WebM). Never commit ProRes `.mov` files, `.hyperframes/`, `.thumbnails/` or `.waveform-cache/`.
- After changing an asset, render it again and update its README if the files or commands changed.
- Episodes are made by `final/make_final.py` from `raw/`. An existing episode folder may hold edits made in the Studio: never pass `--force` to remake it without asking.
