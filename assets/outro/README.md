# BrAIan outro

A 9-second outro to put at the end of our videos. Look at it in [`outro.preview.mp4`](outro.preview.mp4).

1. The first three seconds are the intro's: the mascot lands with the sound logo, slides left as "BrAIan" opens beside it, "AI" lights up and the punch line types itself in (0–2.95 s).
2. The lockup rises and settles at 78 % of its size (3.3–3.95 s).
3. Under it, in a centred column: the website slides in (3.75 s), `npx braian` types itself into a terminal-style prompt (3.95–4.6 s), and the X handle slides in (4.4 s).
4. Everything holds, then fades to black (8.1–8.9 s).

1920 × 1080, 30 fps. The sound is the intro's sound logo, struck as the mascot lands (see `../intro/sound-sets/`). The mix measures −15.4 LUFS with a −1.0 dBTP peak.

## Files

| File | For |
| --- | --- |
| `outro.preview.mp4` | Looking at the outro: the same file as the 1080p master |
| `renders/braian-outro-1080p.mp4` | The master: H.264 + AAC, for uploads and most editors |
| `renders/braian-outro-720p.mp4` | Smaller copies |
| `renders/braian-outro-1080p.webm` | The web: VP9 + Opus |
| `renders/braian-outro-1080p-prores.mov` | Editing: ProRes 422 HQ + PCM. Not committed (144 MB); make it with the command below |
| `index.html` | The root composition: the scene and the sound logo |
| `compositions/card.html` | The picture: the intro's lockup plus the rise and the links |
| `assets/` | The mascot and the sound logo, copied from the intro |

The website, the command and the X handle are variables of the scene (`url`, `command`, `handle`), next to the intro's punch line and accent colour, so they can be changed in the Studio without touching the code.

## Edit and render

`compositions/card.html` started as a copy of the intro's: a change to the shared lockup (the mascot, the name, the punch line) has to be made in both.

```sh
cd assets/outro
export HYPERFRAMES_NO_TELEMETRY=1
npx hyperframes@0.9.41 preview --background          # http://localhost:3002/#project/outro
npx hyperframes@0.9.41 check
npx hyperframes@0.9.41 render --quality delivery -o renders/braian-outro-1080p.mp4
cp renders/braian-outro-1080p.mp4 outro.preview.mp4
cd renders
ffmpeg -y -i braian-outro-1080p.mp4 -vf scale=1280:720:flags=lanczos -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -c:a copy -movflags +faststart braian-outro-720p.mp4
ffmpeg -y -i braian-outro-1080p.mp4 -c:v libvpx-vp9 -crf 28 -b:v 0 -row-mt 1 -c:a libopus -b:a 160k braian-outro-1080p.webm
ffmpeg -y -i braian-outro-1080p.mp4 -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le -c:a pcm_s16le braian-outro-1080p-prores.mov
```
