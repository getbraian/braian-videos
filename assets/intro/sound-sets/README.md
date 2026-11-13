# Sound logo candidates

How the intro's sound logo was chosen, and how to make it again.

**The opening asset is `kept/24-full-synced.wav`**: a vibraphone chord (E, B, E) over a full, pitched low E (a sub that drops into E1 within about 50 ms, doubled an octave up and gently saturated) whose loudness follows the chord's own fade, so the two die away together. `../assets/sfx/braian-logo.wav` is this file cut to the sound itself.

| Folder or file | What |
| --- | --- |
| `index.html` | The listening page: each favourite timed to the mascot landing and to "BrAIan" opening. Serve this folder (for example `python3 -m http.server -d .`) and open it |
| `kept/` | The four favourites (`.wav` stem on the 5 s timeline, `.mp3` levelled, `.mp4` on the picture): the reference copies |
| `aligned/` | The same four, moved so they strike as "BrAIan" opens (1.6 s) |
| `ref/0-current.*` | The previous sound, used as the loudness reference |
| `make_sounds.py` | Synthesizes the candidates from scratch (numpy + scipy) and places them on the timeline |

Every sound was made in code, so none needs credit or a licence.

## Making them again

```sh
python3 -m venv /tmp/snd && /tmp/snd/bin/pip install numpy scipy
/tmp/snd/bin/python make_sounds.py ..          # writes stems/<name>.wav
```

`stems/24-full-synced.wav` comes out identical to `kept/24-full-synced.wav`. The other three can differ slightly in their reverb texture (the noise depends on what was made before), so `kept/` holds the reference copies.

The `.mp3` and `.mp4` files were made from the stems with ffmpeg: a gain that brings the loudest moment to the previous sound's (capped so the peak stays under −1 dBFS, no limiter), then muxed onto `../renders/braian-intro-1080p.mp4`.
