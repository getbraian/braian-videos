# braian-videos

Video material for BrAIan: the brand pieces every video uses, and the reusable video assets (intro, outro, …), each kept as an editable HyperFrames project (HTML, CSS and seekable animations rendered to MP4).

| Folder | What |
| --- | --- |
| [`logo/`](logo) | The brain mascot at 512 px, the master every video and app icon is scaled from |
| [`assets/`](assets) | The reusable video assets, one folder each |
| [`assets/intro/`](assets/intro) | The 5-second intro for the start of our videos: look at [`intro.preview.mp4`](assets/intro/intro.preview.mp4) |
| [`assets/outro/`](assets/outro) | The 9-second outro for the end: the logo, then `npx braian`, the website and the X handle beside it. Look at [`outro.preview.mp4`](assets/outro/outro.preview.mp4) |
| [`.agents/skills/`](.agents/skills) | The HyperFrames agent skills, vendored from HeyGen; Claude Code reads them through `.claude/skills` |

## Assets

Each asset is a folder in `assets/`, made with `npx hyperframes@0.9.41 init <name>` and built like `assets/intro/`:

- **`<name>.preview.mp4`** at the top of the folder: the one file to open to look at the asset (`intro.preview.mp4`, `outro.preview.mp4`, …).
- Everything needed to make it again, committed beside it: the compositions, its media in `assets/`, and any sound or picture experiments that led to it.
- Its delivery renders in `renders/` (MP4 and WebM).
- A README saying what it is and how to render it again.

Shared media comes from `logo/` or the asset's own `assets/`.

Large editing copies (ProRes `.mov`) and HyperFrames' caches are not committed; each README gives the command that makes them.

## Requirements

Node 22+ (for `npx hyperframes`) and `ffmpeg` for the extra encodes.
