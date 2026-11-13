# BrAIan intro

A 5-second intro to put at the start of our videos. Look at it in [`intro.preview.mp4`](intro.preview.mp4).

1. The mascot sweeps in from a blur and lands in the centre of the frame (0.2–0.8 s).
2. It slides left; to its right a 1 px line draws across and opens from its middle into "BrAIan" (1.15–1.83 s).
3. "AI" lights up in the accent colour (1.85 s).
4. The punch line types itself one character at a time behind an accent caret (2.1–2.95 s), and everything holds.
5. Everything fades to black (4.1–4.9 s).

The finished lockup (mascot, then the name over the punch line) is centred. 1920 × 1080, 30 fps.

The sound logo is one sound, struck as the mascot lands: a vibraphone chord (E, B, E) over a full, pitched low E whose fade follows the chord's, so both die away together over about 3 s. It was made in code, not taken from a library; [`sound-sets/`](sound-sets) has how, and the other candidates. The mix measures −15.4 LUFS with a −1.0 dBTP peak.

## Files

| File | For |
| --- | --- |
| `intro.preview.mp4` | Looking at the intro: the same file as the 1080p master |
| `renders/braian-intro-1080p.mp4` | The master: H.264 + AAC, for uploads and most editors |
| `renders/braian-intro-720p.mp4` | Smaller copies |
| `renders/braian-intro-1080p.webm` | The web: VP9 + Opus |
| `renders/braian-intro-1080p-prores.mov` | Editing (Final Cut, Premiere, DaVinci): ProRes 422 HQ + PCM. Not committed (80 MB); make it with the command below |
| `index.html` | The root composition: the scene and the sound logo |
| `compositions/card.html` | The picture. The punch line and the accent colour are variables of this scene |
| `assets/sfx/braian-logo.wav` | The sound logo, cut to the sound itself |
| `assets/sfx/whoosh-short.mp3`, `impact-bass-1.mp3` | The previous sound (HyperFrames library, Pixabay Content License), kept for reference |
| `sound-sets/` | The sound logo's candidates, their listening page and the script that makes them |

## Edit and render

`MARK_SHIFT` in `compositions/card.html` is half the words' width plus the gap, measured with the default punch line: change it if the punch line or the type size changes, so the mascot still lands in the centre.

```sh
cd assets/intro
export HYPERFRAMES_NO_TELEMETRY=1
npx hyperframes@0.9.41 preview --background          # http://localhost:3002/#project/intro
npx hyperframes@0.9.41 check
npx hyperframes@0.9.41 render --quality delivery -o renders/braian-intro-1080p.mp4
cp renders/braian-intro-1080p.mp4 intro.preview.mp4
cd renders
ffmpeg -y -i braian-intro-1080p.mp4 -vf scale=1280:720:flags=lanczos -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -c:a copy -movflags +faststart braian-intro-720p.mp4
ffmpeg -y -i braian-intro-1080p.mp4 -c:v libvpx-vp9 -crf 28 -b:v 0 -row-mt 1 -c:a libopus -b:a 160k braian-intro-1080p.webm
ffmpeg -y -i braian-intro-1080p.mp4 -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le -c:a pcm_s16le braian-intro-1080p-prores.mov
```

The mascot is 512 px (`../logo`) and shown at 380 px, so it has a little room to grow, but a 4K render needs a larger master first.
