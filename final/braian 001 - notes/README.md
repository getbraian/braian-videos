# braian 001 - notes

Episode 001, "Notes": the intro, a title card, `raw/braian 001 - notes.mp4`, the outro, with music. Look at it in [`braian 001 - notes.mp4`](<braian 001 - notes.mp4>); [`braian 001 - notes.png`](<braian 001 - notes.png>) is its cover (1280 × 720, for YouTube): the title card's final frame.

`index.html` is the edit, a HyperFrames project: the title card pushes in and dissolves into the clip, and the clip dips to black into the outro. The title card is `compositions/title.html`: its title and episode label are variables, so they can be changed in the Studio. The clip runs 54.0333 s, over the intro's ground where it doesn't fill the frame.

The music is "Raising Me Higher" from Mixkit (`assets/music.mp3`). It starts with the title card, whose reveals fall on its beats (110 BPM), drops to a bed under the voice when the clip starts, rises again as the clip ends, and fades out over the outro's first seconds. The outro plays without its own logo sound, so the music carries it.

```sh
cd "final/braian 001 - notes"
export HYPERFRAMES_NO_TELEMETRY=1
npx hyperframes@0.9.41 preview --background
npx hyperframes@0.9.41 check
npx hyperframes@0.9.41 render --quality delivery -o "braian 001 - notes.mp4"
```

Or, from the repository root, `python3 final/make_final.py --force --render` remakes every episode and renders it with its cover (losing edits to `index.html` and `compositions/title.html`).

`assets/clip.mp4` is a link to the raw file; `assets/intro.mp4` and `assets/outro.mp4` are copies of their 1080p renders, so a later change to the intro or outro reaches this episode only when they are copied again.
