"""Set up one editable HyperFrames project per raw clip: intro, title card, clip, outro, with music.

usage:  python3 final/make_final.py [--force] [--render]        (from the repository root)

For every raw/<name>.mp4 it makes final/<name>/:
    index.html               the edit: the intro (5 s), the title card, the clip, the outro (9 s), and the music
    compositions/title.html  the title card: the logo and the episode's title, revealed to the music's beat
    assets/intro.mp4         a copy of assets/intro/renders/braian-intro-1080p.mp4
    assets/outro.mp4         a copy of assets/outro/renders/braian-outro-1080p.mp4
    assets/clip.mp4          a link to ../../../raw/<name>.mp4 (not a copy)
    assets/music.mp3         a copy of assets/audio/mixkit-raising-me-higher-34.mp3
    assets/mascot.png        the mascot, from the intro
    package.json, hyperframes.json, meta.json, README.md
An existing project is left alone (it may have been edited) unless --force is given.
With --render it also renders <name>.mp4 and exports the title card's final frame as <name>.png (the cover).

The music ("Raising Me Higher", Mixkit) is 110 BPM: a beat every 0.545 s, the drums in at 2.16 s. It starts with the
title card; the logo resolves on the first beat (0.52 s), the title lands on the drums (2.16 s) and the card cuts to
the clip on the downbeat at 6.533 s. Under the clip the music drops to a bed under the voice and fades out before
the outro.
"""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INTRO = REPO / "assets/intro/renders/braian-intro-1080p.mp4"
OUTRO = REPO / "assets/outro/renders/braian-outro-1080p.mp4"
MUSIC = REPO / "assets/audio/mixkit-raising-me-higher-34.mp3"
MASCOT = REPO / "assets/intro/assets/mascot.png"
W, H, FPS = 1920, 1080, 30
TITLE_CARD = 6.5333          # 196 frames: ends on the music's downbeat at 6.53 s
MUSIC_TITLE_VOL = 0.62       # about -16 LUFS under the title card, close to the intro and the voice (-15.4)
MUSIC_BED_VOL = 0.085        # about -31 LUFS under the clip: some 15 dB under the voice
CROSS = 0.6                  # the music's drop from title level to bed level, as the clip starts
T_IN = 0.8                   # the title card dissolves into the clip over its last 0.8 s, the clip fully in on the downbeat
T_OUT = 1.0                  # the clip dips to black over its last 1.0 s; the outro then rises out of its own black
SWELL = 1.5                  # the music rises from bed level back up over the clip's last 1.5 s ...
MUSIC_END_VOL = 0.5          # ... to this level as the outro starts ...
MUSIC_END_FADE = 6.0         # ... and fades out over the outro's first 6 s
OUTRO_SOUND = False          # the outro's own logo sound: off, so the music alone carries the outro


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    s = d["streams"][0] if d.get("streams") else {"width": 0, "height": 0}
    return s["width"], s["height"], float(d["format"]["duration"])


def seconds(x):  # whole frames, so every cut lands on a frame
    return round(round(x * FPS) / FPS, 4)


def episode_of(name):
    """'braian 001 - notes' -> ('001', 'Notes'); 'braian 002 - code vault' -> ('002', 'Code Vault')."""
    m = re.match(r".*?(\d+)\s*-\s*(.+)$", name)
    num, title = (m.group(1), m.group(2)) if m else ("", name)
    return num, " ".join(w[:1].upper() + w[1:] for w in title.split())


TITLE_HTML = r'''<html
  data-composition-variables='[
    {"id":"title","type":"string","label":"Title","default":"__TITLE__","maxLength":28},
    {"id":"episode","type":"string","label":"Episode","default":"__EPISODE__","maxLength":24}
  ]'
>
  <template>
    <style>
      #root {
        position: absolute;
        inset: 0;
        overflow: hidden;
        font-family: "Inter", sans-serif;
        --accent: #4daafc;
        --ink: #ffffff;
        --muted: #aab3c8;
      }
      /* The intro's ground, then a vignette that darkens the edges like a film frame. */
      #tc-ground {
        position: absolute;
        inset: 0;
        background: radial-gradient(ellipse 70% 80% at 50% 42%, #283562 0%, #141c3a 55%, #0b1024 100%);
        opacity: 0;
      }
      #tc-vignette {
        position: absolute;
        inset: 0;
        background: radial-gradient(ellipse 75% 70% at 50% 50%, transparent 55%, rgba(0, 0, 0, 0.55) 100%);
      }
      #tc-glow {
        position: absolute;
        left: 610px;
        top: 150px;
        width: 700px;
        height: 480px;
        border-radius: 50%;
        background: radial-gradient(ellipse, var(--accent) 0%, transparent 65%);
        opacity: 0;
      }
      /* Everything that is pushed in slowly, like a camera move. */
      #tc-stage {
        position: absolute;
        inset: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
      }
      #tc-lockup {
        display: flex;
        align-items: center;
        gap: 24px;
      }
      #tc-mascot {
        width: 120px;
        height: 120px;
        display: block;
      }
      #tc-words {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
      }
      #tc-tagline {
        margin: 8px 0 0 3px;
        color: var(--muted);
        font-size: 28px;
        font-weight: 400;
        letter-spacing: -0.01em;
        line-height: 1.2;
        white-space: nowrap;
      }
      #tc-name {
        margin: 0;
        color: var(--ink);
        font-size: 68px;
        font-weight: 900;
        letter-spacing: -0.035em;
        line-height: 1;
      }
      .tc-ai {
        color: var(--accent);
        text-shadow: 0 0 28px rgba(77, 170, 252, 0.55);
      }
      #tc-line {
        margin-top: 34px;
        width: 360px;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--accent), transparent);
        opacity: 0;
      }
      #tc-episode {
        margin: 34px 0 0;
        color: var(--accent);
        font-size: 28px;
        font-weight: 700;
        letter-spacing: 0.32em;
        text-transform: uppercase;
        line-height: 1;
        padding-left: 0.32em;
      }
      #tc-title-box {
        position: relative;
        margin-top: 26px;
      }
      #tc-title {
        margin: 0;
        color: var(--ink);
        font-size: 120px;
        font-weight: 900;
        letter-spacing: -0.03em;
        line-height: 1.05;
        white-space: nowrap;
      }
      #tc-title span {
        display: inline-block;
      }
      /* A band of light that sweeps across the title once it has landed. */
      #tc-sweep {
        position: absolute;
        inset: 0;
        margin: 0;
        font-size: 120px;
        font-weight: 900;
        letter-spacing: -0.03em;
        line-height: 1.05;
        white-space: nowrap;
        color: transparent;
        background: linear-gradient(100deg, transparent 0%, transparent 40%, rgba(170, 215, 255, 0.95) 50%, transparent 60%, transparent 100%);
        background-size: 300% 100%;
        background-position: 100% 0;
        -webkit-background-clip: text;
        background-clip: text;
      }
    </style>

    <div id="root" data-composition-id="title" data-width="1920" data-height="1080">
      <div id="tc-ground"></div>
      <div id="tc-glow"></div>
      <div id="tc-stage">
        <div id="tc-lockup">
          <img id="tc-mascot" src="assets/mascot.png" alt="BrAIan" />
          <div id="tc-words">
            <h2 id="tc-name">Br<span class="tc-ai">AI</span>an</h2>
            <p id="tc-tagline">Your second brain, wired.</p>
          </div>
        </div>
        <div id="tc-line"></div>
        <p id="tc-episode" data-var-text="episode">__EPISODE__</p>
        <div id="tc-title-box" data-layout-allow-overlap>
          <h1 id="tc-title" aria-label="__TITLE__"></h1>
          <p id="tc-sweep" aria-hidden="true" data-layout-allow-overlap data-layout-ignore></p>
        </div>
      </div>
      <div id="tc-vignette"></div>
    </div>

    <script>
      const tl = gsap.timeline({ paused: true });
      const v = window.__hyperframes?.getVariables?.() || {};
      const title = v.title || "__TITLE__";

      // the title as one span per letter, so each can rise on its own; the sweep layer carries the same text
      const titleEl = document.querySelector("#tc-title");
      titleEl.textContent = "";
      for (const ch of title) {
        const s = document.createElement("span");
        s.className = "tc-ch";
        s.textContent = ch === " " ? " " : ch;
        titleEl.appendChild(s);
      }
      document.querySelector("#tc-sweep").textContent = title;

      // 0–0.9  the ground comes up out of black; a slow push-in (1.06 to 1) runs under everything and settles by 5.6
      tl.fromTo("#tc-ground", { opacity: 0 }, { opacity: 1, duration: 0.9, ease: "power2.out" }, 0);
      tl.fromTo("#tc-stage", { scale: 1.06 }, { scale: 1, duration: 5.6, ease: "power2.out" }, 0);

      // 0.52  first beat: the logo resolves out of a blur, the glow blooms behind it
      tl.fromTo("#tc-lockup", { opacity: 0, filter: "blur(18px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.9, ease: "power2.out" }, 0.52);
      tl.fromTo("#tc-glow", { opacity: 0, scale: 0.7 }, { opacity: 0.22, scale: 1, duration: 1.4, ease: "expo.out" }, 0.52);

      // 1.07  second beat: a thin accent line draws out from the centre
      tl.fromTo("#tc-line", { opacity: 0, scaleX: 0 }, { opacity: 1, scaleX: 1, duration: 0.7, ease: "expo.out" }, 1.07);

      // 1.61  third beat: the episode label settles in, from wide and soft to its size
      tl.fromTo("#tc-episode", { opacity: 0, scale: 1.12, filter: "blur(6px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 1.0, ease: "power3.out" }, 1.61);

      // 2.16  the drums: the title rises letter by letter out of a blur
      tl.fromTo(".tc-ch", { opacity: 0, y: 48, filter: "blur(14px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.55, ease: "power4.out", stagger: 0.035 }, 2.16);

      // 2.75–3.65  a band of light sweeps across the landed title
      tl.fromTo("#tc-sweep", { backgroundPosition: "100% 0" }, { backgroundPosition: "0% 0", duration: 0.9, ease: "power2.inOut" }, 2.75);

      // 3.65–__HOLD_END__  it holds; from 5.6 nothing moves, and that still frame is the episode's cover

      // __HOLD_END__–6.53  the exit: the card pushes in, blurs and fades while the clip dissolves in over it
      tl.to("#tc-stage", { scale: 1.08, opacity: 0, filter: "blur(12px)", duration: __T_IN__, ease: "power2.in" }, __HOLD_END__);
      tl.to("#tc-glow", { opacity: 0, duration: __T_IN__, ease: "power2.in" }, __HOLD_END__);

      window.__timelines["title"] = tl;
    </script>
  </template>
</html>
'''


def index_html(name, clip_w, clip_h, clip_dur):
    intro, outro = probe(INTRO)[2], probe(OUTRO)[2]
    clip_dur = seconds(clip_dur)
    t0 = seconds(intro)                       # the title card starts
    c0 = seconds(intro + TITLE_CARD - T_IN)   # the clip starts dissolving in; fully in on the downbeat at t0 + TITLE_CARD
    o0 = seconds(c0 + clip_dur)               # the outro starts, from black, as the clip ends
    sw = seconds(o0 - SWELL)                  # the music starts rising back up
    total = seconds(o0 + outro)
    scale = W / clip_w
    ch = round(clip_h * scale)
    top = (H - ch) // 2
    return f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }}
      html,
      body {{
        margin: 0;
        width: {W}px;
        height: {H}px;
        overflow: hidden;
        background: #000;
      }}
      #root {{
        width: 100%;
        height: 100%;
      }}
      /* The ground behind the clip: the intro's own gradient, so any room above and below the clip matches the brand. */
      #ground {{
        position: absolute;
        inset: 0;
        background: radial-gradient(ellipse 70% 80% at 50% 42%, #283562 0%, #141c3a 55%, #0b1024 100%);
      }}
      .full {{
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
      }}
      /* The clip and the outro sit in wrappers that the root timeline dissolves; the videos themselves are timed. */
      #clip-wrap,
      #outro-wrap {{
        position: absolute;
        inset: 0;
      }}
      #clip {{
        position: absolute;
        left: 0;
        top: {top}px;
        width: {W}px;
        height: {ch}px;
        object-fit: contain;
      }}
    </style>
  </head>
  <body>
    <!-- {name}: intro 0–{t0} s, title card from {t0} s, dissolving into the clip from {c0} s, which dips to black
         into the outro at {o0} s; {total} s in all.
         To trim the clip, change its data-media-start (where it starts in the file) and data-duration, then move the
         outro's data-start, the music bed's data-duration and the root's data-duration to match. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}">
      <video id="intro" class="clip full" src="assets/intro.mp4" data-start="0" data-duration="{t0}" data-track-index="1" data-has-audio="true"></video>
      <div
        id="title"
        data-composition-id="title"
        data-composition-src="compositions/title.html"
        data-start="{t0}"
        data-duration="{TITLE_CARD}"
        data-track-index="2"
        data-track-kind="graphics"
        data-width="{W}"
        data-height="{H}"
      ></div>
      <div id="clip-wrap">
        <div id="ground" class="clip" data-start="{c0}" data-duration="{clip_dur}" data-track-index="3"></div>
        <video id="clip" class="clip" src="assets/clip.mp4" data-start="{c0}" data-media-start="0" data-duration="{clip_dur}" data-track-index="4" data-has-audio="true"></video>
      </div>
      <!-- The outro plays without its own logo sound ({'on' if OUTRO_SOUND else 'muted'}): the music carries it. For the logo sound, swap muted for data-has-audio="true". -->
      <div id="outro-wrap">
        <video id="outro" class="clip full" src="assets/outro.mp4" data-start="{o0}" data-duration="{seconds(outro)}" data-track-index="5" {'data-has-audio="true"' if OUTRO_SOUND else 'muted'}></video>
      </div>

      <!-- The music, one track played as three overlapping pieces that stay in step (each starts in the file at its
           time minus {t0} s): at title level under the title card; dropping to a bed under the clip's voice over {CROSS} s;
           rising back over the clip's last {SWELL} s, and fading out over the outro's first {MUSIC_END_FADE} s. -->
      <audio id="music-title" class="clip" src="assets/music.mp3" data-start="{t0}" data-media-start="0" data-duration="{seconds(c0 - t0 + CROSS)}" data-volume="{MUSIC_TITLE_VOL}" data-fade-out="{CROSS}" data-track-index="6"></audio>
      <audio id="music-bed" class="clip" src="assets/music.mp3" data-start="{c0}" data-media-start="{seconds(c0 - t0)}" data-duration="{seconds(o0 - c0)}" data-volume="{MUSIC_BED_VOL}" data-fade-in="{CROSS}" data-fade-out="{SWELL}" data-track-index="7"></audio>
      <audio id="music-end" class="clip" src="assets/music.mp3" data-start="{sw}" data-media-start="{seconds(sw - t0)}" data-duration="{seconds(SWELL + MUSIC_END_FADE)}" data-volume="{MUSIC_END_VOL}" data-fade-in="{SWELL}" data-fade-out="{MUSIC_END_FADE}" data-track-index="8"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      // into the clip: it settles in (from 104 % and transparent) while the title card pushes in and blurs away under it
      tl.fromTo("#clip-wrap", {{ opacity: 0, scale: 1.04 }}, {{ opacity: 1, scale: 1, duration: {T_IN}, ease: "power2.out" }}, {c0});
      // out of the clip: it eases back and dips to black over its last {T_OUT} s; the outro rises out of its own black
      tl.to("#clip-wrap", {{ opacity: 0, scale: 1.03, duration: {T_OUT}, ease: "power2.in" }}, {seconds(o0 - T_OUT)});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''


def readme(name, num, title, clip_dur):
    return f'''# {name}

Episode {num}, "{title}": the intro, a title card, `raw/{name}.mp4`, the outro, with music. Look at it in [`{name}.mp4`](<{name}.mp4>); [`{name}.png`](<{name}.png>) is its cover (1280 × 720, for YouTube): the title card's final frame.

`index.html` is the edit, a HyperFrames project: the title card pushes in and dissolves into the clip, and the clip dips to black into the outro. The title card is `compositions/title.html`: its title and episode label are variables, so they can be changed in the Studio. The clip runs {seconds(clip_dur)} s, over the intro's ground where it doesn't fill the frame.

The music is "Raising Me Higher" from Mixkit (`assets/music.mp3`). It starts with the title card, whose reveals fall on its beats (110 BPM), drops to a bed under the voice when the clip starts, rises again as the clip ends, and fades out over the outro's first seconds. The outro plays without its own logo sound, so the music carries it.

```sh
cd "final/{name}"
export HYPERFRAMES_NO_TELEMETRY=1
npx hyperframes@0.9.41 preview --background
npx hyperframes@0.9.41 check
npx hyperframes@0.9.41 render --quality delivery -o "{name}.mp4"
```

Or, from the repository root, `python3 final/make_final.py --force --render` remakes every episode and renders it with its cover (losing edits to `index.html` and `compositions/title.html`).

`assets/clip.mp4` is a link to the raw file; `assets/intro.mp4` and `assets/outro.mp4` are copies of their 1080p renders, so a later change to the intro or outro reaches this episode only when they are copied again.
'''


force = "--force" in sys.argv
made = []
for raw in sorted((REPO / "raw").glob("*.mp4")):
    name = raw.stem
    proj = REPO / "final" / name
    num, title = episode_of(name)
    if proj.exists() and not force:
        print("exists, left alone:", name); made.append((name, proj)); continue
    (proj / "assets").mkdir(parents=True, exist_ok=True)
    (proj / "compositions").mkdir(exist_ok=True)
    shutil.copy2(INTRO, proj / "assets/intro.mp4")
    shutil.copy2(OUTRO, proj / "assets/outro.mp4")
    shutil.copy2(MUSIC, proj / "assets/music.mp3")
    shutil.copy2(MASCOT, proj / "assets/mascot.png")
    link = proj / "assets/clip.mp4"
    if link.is_symlink() or link.exists(): link.unlink()
    link.symlink_to(os.path.relpath(raw, link.parent))
    cw, ch, cd = probe(raw)
    (proj / "index.html").write_text(index_html(name, cw, ch, cd))
    episode = f"Episode {num}" if num else "BrAIan"
    hold_end = seconds(TITLE_CARD - T_IN)
    (proj / "compositions/title.html").write_text(TITLE_HTML.replace("__TITLE__", title).replace("__EPISODE__", episode)
                                                  .replace("__HOLD_END__", str(hold_end)).replace("__T_IN__", str(T_IN)))
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    (proj / "meta.json").write_text(json.dumps({"id": slug, "name": name, "createdAt": "2026-11-13T17:10:00.000Z"}, indent=2) + "\n")
    pkg = json.loads((REPO / "assets/outro/package.json").read_text()); pkg["name"] = slug
    (proj / "package.json").write_text(json.dumps(pkg, indent=2) + "\n")
    shutil.copy2(REPO / "assets/outro/hyperframes.json", proj / "hyperframes.json")
    shutil.copy2(REPO / "assets/outro/.gitignore", proj / ".gitignore")
    (proj / "README.md").write_text(readme(name, num, title, cd))
    for old in ["final.mp4"]:
        if (proj / old).exists(): (proj / old).unlink()
    print("made:", name, f'(episode {num}, "{title}", {cw}x{ch}, {cd:.2f} s)')
    made.append((name, proj))

if "--render" in sys.argv:
    env = dict(os.environ, HYPERFRAMES_NO_TELEMETRY="1")
    CLI = ["npx", "--yes", "hyperframes@0.9.41"]
    cover_at = seconds(probe(INTRO)[2] + TITLE_CARD - T_IN - 1 / FPS)     # the title card's last still frame, before its exit
    for name, proj in made:
        chk = subprocess.run(CLI + ["check"], cwd=proj, env=env, capture_output=True, text=True).stdout
        bad = [l for l in chk.splitlines() if "✗" in l]
        print(name, "check:", "passed" if not bad else "\n  " + "\n  ".join(bad))
        subprocess.run(CLI + ["render", "--quality", "delivery", "-o", f"{name}.mp4"], cwd=proj, env=env, check=True, capture_output=True)
        snap = proj / ".hyperframes/cover"
        if snap.exists(): shutil.rmtree(snap)
        subprocess.run(CLI + ["snapshot", "--at", str(cover_at), "--no-end", "-o", str(snap)], cwd=proj, env=env, check=True, capture_output=True)
        frame = next(snap.glob("frame-*.png"))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(frame), "-vf", "scale=1280:720:flags=lanczos", str(proj / f"{name}.png")], check=True)
        print(name, "rendered, cover at", cover_at, "s")
