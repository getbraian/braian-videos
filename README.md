# braian-videos

Video material for BrAIan: the brand pieces every video uses, the reusable video assets (intro, outro, …), and the finished episodes, each kept as an editable HyperFrames project (HTML, CSS and seekable animations rendered to MP4).

| Folder | What |
| --- | --- |
| [`assets/logo/`](assets/logo) | The brain mascot at 512 px, the master every video and app icon is scaled from |
| [`assets/intro/`](assets/intro) | The 5-second intro for the start of our videos: look at [`intro.preview.mp4`](assets/intro/intro.preview.mp4) |
| [`assets/outro/`](assets/outro) | The 9-second outro for the end: the logo, then `npx braian`, the website and the X handle beside it. Look at [`outro.preview.mp4`](assets/outro/outro.preview.mp4) |
| [`assets/audio/`](assets/audio) | Music for the episodes: "Raising Me Higher" from Mixkit |
| [`raw/`](raw) | The episodes' raw recordings, one file each, as recorded |
| [`final/`](final) | The finished episodes, one folder per raw recording: `<name>.mp4` to upload and `<name>.png`, its cover |
| [`.agents/skills/`](.agents/skills) | The HyperFrames agent skills, vendored from HeyGen; Claude Code reads them through `.claude/skills` |

## Assets

Each asset is a folder in `assets/`, made with `npx hyperframes@0.9.41 init <name>` and built like `assets/intro/`:

- **`<name>.preview.mp4`** at the top of the folder: the one file to open to look at the asset (`intro.preview.mp4`, `outro.preview.mp4`, …).
- Everything needed to make it again, committed beside it: the compositions, its media in `assets/`, and any sound or picture experiments that led to it.
- Its delivery renders in `renders/` (MP4 and WebM).
- A README saying what it is and how to render it again.

Shared media comes from `assets/logo/`, `assets/audio/` or the asset's own `assets/`.

## Episodes

Drop a recording into `raw/` as `<name>.mp4` (for example `braian 003 - graph.mp4`: the number and the words after the dash become the episode label and title) and run, from the repository root:

```sh
python3 final/make_final.py --render
```

It sets up `final/<name>/`, an editable HyperFrames project (the intro, a title card timed to the music, the clip, the outro), renders `final/<name>/<name>.mp4` and exports the title card's last frame as `final/<name>/<name>.png`, the YouTube cover. An episode folder that already exists is left alone, so edits made in the Studio are kept; `--force` remakes it. Each folder's README says how to edit and render it.

Large editing copies (ProRes `.mov`) and HyperFrames' caches are not committed; each README gives the command that makes them.

## Requirements

Node 22+ (for `npx hyperframes`), `ffmpeg` for the extra encodes, and Python 3 for `final/make_final.py`.
