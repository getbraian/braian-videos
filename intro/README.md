# BrAIan intro

A 5-second intro to put at the start of our videos: the mascot sweeps in and lands, "BrAIan" arrives letter by letter with "AI" lighting up in the accent colour, the punch line blurs in, and everything fades to black. 1920 × 1080, 30 fps.

The sound logo is three effects from the HyperFrames bundled library (Pixabay Content License, no attribution needed): a whoosh as the mascot moves, a bass hit as it lands and a sparkle as "AI" lights up. The mix measures −13 LUFS with a −4.3 dBTP peak.

## Files

| File | For |
| --- | --- |
| `renders/braian-intro-1080p.mp4` | The master: H.264 + AAC, for uploads and most editors |
| `renders/braian-intro-720p.mp4` | Smaller copies |
| `renders/braian-intro-1080p.webm` | The web: VP9 + Opus |
| `renders/braian-intro-1080p-prores.mov` | Editing (Final Cut, Premiere, DaVinci): ProRes 422 HQ + PCM. Not committed (81 MB); make it with the command below |

## Edit and render

`index.html` holds the sound; `compositions/card.html` the picture. The punch line and the accent colour are variables of that scene.

```sh
cd intro
export HYPERFRAMES_NO_TELEMETRY=1
npx hyperframes@0.9.41 preview --background          # http://localhost:3002/#project/intro
npx hyperframes@0.9.41 check
npx hyperframes@0.9.41 render --quality delivery -o renders/braian-intro-1080p.mp4
cd renders
ffmpeg -y -i braian-intro-1080p.mp4 -vf scale=1280:720:flags=lanczos -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -c:a copy -movflags +faststart braian-intro-720p.mp4
ffmpeg -y -i braian-intro-1080p.mp4 -c:v libvpx-vp9 -crf 28 -b:v 0 -row-mt 1 -c:a libopus -b:a 160k braian-intro-1080p.webm
ffmpeg -y -i braian-intro-1080p.mp4 -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le -c:a pcm_s16le braian-intro-1080p-prores.mov
```

The mascot is 512 px (`../logo`), so it cannot grow much past its current 440 px without blurring, and a 4K render needs a larger master first.
