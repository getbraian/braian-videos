# braian-videos

Video material for BrAIan: the brand pieces every video uses, and the source of each video, kept as editable HyperFrames projects (HTML, CSS and seekable animations rendered to MP4).

| Folder | What |
| --- | --- |
| [`logo/`](logo) | The brain mascot at 512 px, the master every video and app icon is scaled from |
| [`intro/`](intro) | The 5-second intro for the start of our videos, with its renders in `intro/renders` |
| [`.agents/skills/`](.agents/skills) | The HyperFrames agent skills, vendored from HeyGen; Claude Code reads them through `.claude/skills` |

## Adding a video

Each video is a folder at the top level, made with `npx hyperframes@0.9.41 init <name>` and built like `intro/`: its sources committed, its finished renders in `<name>/renders` (MP4 and WebM), and a README saying what it is and how to render it again. Shared media comes from `logo/` or the video's own `assets/`.

Large editing copies (ProRes `.mov`) and HyperFrames' caches are not committed; each README gives the command that makes them.

## Requirements

Node 22+ (for `npx hyperframes`) and `ffmpeg` for the extra encodes.
