"""The sound candidates for the BrAIan intro, synthesized from scratch (numpy + scipy, no samples except
the two library sounds of the old intro), each placed on the intro's 5 s timeline.

usage:  python3 make_sounds.py <assets/intro dir>      writes sound-sets/stems/<name>.wav and sets.json

Every event is anchored on a moment of the picture (seconds), at the sound's attack: the first sample at half its
peak, unless an explicit anchor is given. SETS at the bottom lists the four favourites; the functions above it are
every sound tried along the way. The canonical files are sound-sets/kept/*.wav. Noise is seeded, but each sound's
noise depends on what was made before it: the opening asset (24) is made first and comes out identical to its kept
file; the other three can come out with slightly different reverb texture from their kept files.
"""
import sys, subprocess, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 5.0
intro = sys.argv[1]
LIB = f"{intro}/../../.agents/skills/media-use/audio/assets/sfx"
rng = np.random.default_rng(5)

# ---- the picture's moments (compositions/card.html) ----
ENTER = 0.20      # the mascot starts sweeping in
LAND = 0.633      # it lands: the current bass hit's attack
SLIDE = 1.15      # it slides left (1.15-1.70)
LINE = 1.30       # the 1 px line draws across (1.30-1.48)
OPEN = 1.45       # the line opens into the name (1.45-1.83)
OPENED = 1.80
TYPE0, PER_CHAR, CHARS = 2.10, 0.034, len("Your second brain, wired.")

# ---- helpers ----
def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
def attack(x):
    m = np.abs(x).max(1); return int(np.argmax(m >= 0.5 * m.max()))
def t_(d): return np.arange(int(d * SR)) / SR
def env(t, a, d): return np.minimum(t / a, 1.0) * np.exp(-t / d)
def sweep(t, f0, f1, tau): return np.sin(2 * np.pi * (f1 * t + (f0 - f1) * tau * (1 - np.exp(-t / tau))))
def filt(x, kind, f, o=2): return sosfilt(butter(o, f, kind, fs=SR, output="sos"), x, axis=0)
def st(x, p=0.0): return np.stack([x * np.sqrt((1 - p) / 2), x * np.sqrt((1 + p) / 2)], 1) * np.sqrt(2)
def norm(x, peak=0.9): return x / np.abs(x).max() * peak
def room(x, decay, mix):
    n = int(decay * 3 * SR); tt = np.arange(n) / SR; out = []
    for c in range(2):
        ir = filt(rng.standard_normal(n), "low", 6000) * np.exp(-tt / decay); ir /= np.sqrt((ir ** 2).sum())
        d = np.pad(x[:, c], (0, n)); out.append(d + mix * fftconvolve(d, ir)[: len(d)])
    return np.stack(out, 1)
def db(g): return 10 ** (g / 20)

# ---- synthesized sounds ----
def soft_thud():
    t = t_(0.6); x = sweep(t, 95, 48, 0.06) * env(t, 0.004, 0.13) + 0.25 * filt(rng.standard_normal(len(t)), "low", 400) * env(t, 0.002, 0.03)
    return norm(st(np.tanh(1.4 * filt(x, "low", 900, 4))))
def tight_punch():
    t = t_(0.35)
    x = sweep(t, 170, 55, 0.025) * env(t, 0.0015, 0.07) + 0.45 * filt(rng.standard_normal(len(t)), "band", [1500, 7000]) * env(t, 0.0005, 0.012)
    return norm(st(np.tanh(1.8 * x)))
def deep_boom():
    t = t_(1.6)
    x = np.tanh(2.2 * (sweep(t, 120, 38, 0.09) * env(t, 0.003, 0.45) + 0.35 * sweep(t, 240, 76, 0.05) * env(t, 0.002, 0.08)))
    return norm(room(st(filt(x, "low", 2500, 4)), 0.35, 0.18))
def cinematic_hit():
    t = t_(1.2)
    x = np.tanh(1.6 * (sweep(t, 70, 32, 0.15) * env(t, 0.005, 0.5) + 0.6 * sweep(t, 140, 95, 0.08) * env(t, 0.002, 0.18)
                      + 0.5 * filt(rng.standard_normal(len(t)), "low", 1800) * env(t, 0.001, 0.09)))
    return norm(room(st(x), 0.7, 0.28))
def swish(d=0.5, f0=600, f1=4000, pan0=0.6, pan1=-0.6):
    """Filtered air that moves (and pans) with something sliding: band-passed noise whose centre sweeps."""
    t = t_(d); n = rng.standard_normal(len(t)); out = np.zeros(len(t))
    seg = 480
    for i in range(0, len(t), seg):  # a moving band-pass, block by block
        c = f0 * (f1 / f0) ** (i / len(t))
        out[i:i + seg] = filt(n[max(0, i - 2000):i + seg], "band", [c * 0.7, c * 1.4])[-len(out[i:i + seg]):]
    shape = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    p = np.linspace(pan0, pan1, len(t))
    return norm(np.stack([out * shape * np.sqrt((1 - p) / 2), out * shape * np.sqrt((1 + p) / 2)], 1))
def zip_(d=0.18, f0=900, f1=5200):
    """A thin rising zip for the line drawing across, panned left to right like the line."""
    t = t_(d); x = sweep(t, f0, f1, -d) if False else np.sin(2 * np.pi * (f0 * t + (f1 - f0) * t ** 2 / (2 * d)))
    x = x * np.sin(np.pi * t / d) ** 0.5 * 0.6 + 0.25 * filt(rng.standard_normal(len(t)), "high", 4000) * np.sin(np.pi * t / d)
    p = np.linspace(-0.7, 0.7, len(t))
    return norm(np.stack([x * np.sqrt((1 - p) / 2), x * np.sqrt((1 + p) / 2)], 1))
def swell(d=0.45):
    """A reversed-reverb swell that rises into the moment the name is fully open, then cuts."""
    t = t_(d); tone = sweep(t, 110, 110, 1) + 0.5 * np.sin(2 * np.pi * 165 * t) + 0.3 * filt(rng.standard_normal(len(t)), "band", [300, 2500])
    rise = (t / d) ** 3
    return norm(room(st(tone * rise), 0.25, 0.4)[: len(t)])
def tick(f=3200, d=0.025, body=900):
    """One soft key tick: a short band of noise and a tiny pitched body."""
    t = t_(d + 0.02)
    x = filt(rng.standard_normal(len(t)), "band", [f * 0.6, f * 1.6]) * env(t, 0.0003, d / 5) + 0.5 * np.sin(2 * np.pi * body * t) * env(t, 0.0005, 0.006)
    return st(x / np.abs(x).max())
def typing_track(gain_db, every=1, pitch=1.0, soft=False):
    """One tick per typed character (or every n-th), each a little different, so it reads as typing, not a buzz."""
    out = []
    for i in range(0, CHARS, every):
        k = tick(f=(2200 if soft else 3400) * pitch * (1 + 0.12 * rng.standard_normal()), d=0.03 if soft else 0.02, body=700 * pitch)
        if soft: k = filt(k, "low", 3500)
        out.append((k * db(gain_db + rng.uniform(-3, 0)), TYPE0 + i * PER_CHAR + rng.uniform(0, 0.004), 0))
    return out

# ---- the sets: [(sound, time its attack lands, gain dB)] ----
lib = lambda n: load(f"{LIB}/{n}.mp3")
ownsfx = lambda n: load(f"{intro}/assets/sfx/{n}.mp3")
def tail(x, keep, fade=0.3):
    """Shorten a sound: keep `keep` seconds, then fade out over `fade`."""
    n, f = int(keep * SR), int(fade * SR); x = x[: n + f].copy(); x[n:] *= np.linspace(1, 0, len(x) - n)[:, None]; return x
def deep_boom_dark():
    """The minimal boom, lower and longer, with no upper harmonic: more felt than heard."""
    t = t_(2.2)
    x = np.tanh(1.8 * sweep(t, 95, 32, 0.12) * env(t, 0.004, 0.7))
    return norm(room(st(filt(x, "low", 900, 4)), 0.5, 0.22))
def soft_boom():
    """A lighter echo of the landing boom, for the name opening: same family, an octave up, short."""
    t = t_(0.8)
    x = np.tanh(1.6 * sweep(t, 160, 70, 0.05) * env(t, 0.003, 0.16))
    return norm(room(st(filt(x, "low", 1500, 4)), 0.3, 0.2))
def sub_swell(d=0.5):
    """A sub that rises out of nothing into the landing, instead of a whoosh."""
    t = t_(d); x = sweep(t, 30, 55, 1.0) * (t / d) ** 2.5
    return norm(st(np.tanh(1.5 * x)))

whoosh_in = (ownsfx("whoosh-short"), 0.17 + attack(ownsfx("whoosh-short")) / SR, -8)

# ---- sonic logos: one sound each, original, built around E (E1 41.2 Hz) ----
E1 = 41.2
def partial(t, f, d, a=0.004, detune=0.0):
    return (np.sin(2 * np.pi * f * (1 + detune) * t) + np.sin(2 * np.pi * f * (1 - detune) * t)) / 2 * env(t, a, d)
def hall(x, decay=1.4, mix=0.35): return room(x, decay, mix)
def thump(t, d=0.02, lp=900): return filt(rng.standard_normal(len(t)), "low", lp) * env(t, 0.0005, d)

def logo_resonant():
    """A deep hit that blooms into an open E chord and hangs in a hall: the logo's 'presence'."""
    t = t_(3.0)
    sub = sweep(t, 95, E1, 0.05) * env(t, 0.002, 0.9)
    body = sum(g * partial(t, f, d, 0.01, 0.002) for f, g, d in [(E1 * 2, 0.7, 1.1), (E1 * 3, 0.45, 0.9), (E1 * 4, 0.3, 0.8), (E1 * 6, 0.12, 0.6)])
    x = np.tanh(1.5 * (sub + body + 0.5 * thump(t)))
    return norm(hall(st(filt(x, "low", 3000, 4)), 1.6, 0.35))

def logo_two_step():
    """A soft pickup and a full downbeat a fifth below, 0.22 s apart: a two-step 'ba-DOOM'."""
    t = t_(3.0); g = 0.22
    pick = np.tanh(1.3 * (sweep(t, 150, E1 * 3, 0.03) * env(t, 0.002, 0.12) + 0.4 * thump(t, 0.01, 1500))) * 0.45
    down_t = np.maximum(t - g, 0); on = (t >= g)
    down = on * (sweep(down_t, 100, E1, 0.05) * env(down_t + 1e-9, 0.002, 1.0)
                 + 0.6 * partial(down_t, E1 * 2, 1.2, 0.008, 0.002) + 0.35 * partial(down_t, E1 * 3, 0.9, 0.01, 0.003) + 0.5 * thump(down_t))
    x = np.tanh(1.5 * (pick + down))
    return norm(hall(st(filt(x, "low", 3200, 4)), 1.5, 0.32)), g + 0.003   # anchor: the downbeat

def logo_gong():
    """A deep processed gong: inharmonic metal partials over a sub, slowly beating, a long dark tail."""
    t = t_(3.6); f0 = 55.0
    metal = sum(g * partial(t, f0 * r, d, 0.003, 0.0015 * (k + 1)) for k, (r, g, d) in enumerate(
        [(1.0, 1.0, 1.6), (2.32, 0.55, 1.2), (3.01, 0.3, 0.9), (4.25, 0.25, 0.8), (5.39, 0.15, 0.6), (6.63, 0.1, 0.5)]))
    sub = sweep(t, 80, E1, 0.06) * env(t, 0.003, 0.8)
    x = np.tanh(1.3 * (0.8 * metal + sub + 0.4 * thump(t, 0.015, 2500)))
    return norm(hall(st(filt(x, "low", 4500, 2)), 2.0, 0.3))

def logo_braam():
    """A short trailer 'braam': a low brass-like stack whose filter opens on the hit and closes over 1.5 s."""
    t = t_(2.4)
    saw = lambda f: 2 * ((f * t) % 1) - 1
    stack = sum(g * (saw(f * 1.003) + saw(f * 0.997)) / 2 for f, g in [(E1, 1.0), (E1 * 2, 0.8), (E1 * 3, 0.5), (E1 * 4, 0.3)])
    amp = np.minimum(t / 0.05, 1) * np.exp(-t / 1.1)
    out = np.zeros(len(t)); n = rng.standard_normal(len(t)); seg = 960
    for i in range(0, len(t), seg):  # the filter opens fast and closes slowly
        c = 180 + 2400 * np.exp(-(i / SR) / 0.35)
        out[i:i + seg] = filt(stack[max(0, i - 4000):i + seg], "low", c, 2)[-len(out[i:i + seg]):]
    x = np.tanh(2.0 * out * amp) + 0.6 * sweep(t, 80, E1, 0.05) * env(t, 0.003, 0.7)
    return norm(hall(st(x), 1.3, 0.3)), 0.03

def logo_rise_hit():
    """One gesture: a reversed hall rises with the mascot's sweep and resolves into a deep, clean hit."""
    pre = 0.43   # the rise starts as the mascot appears (0.2 s) and peaks at the landing
    hit_t = t_(2.8)
    hit = np.tanh(1.5 * (sweep(hit_t, 95, E1, 0.05) * env(hit_t, 0.002, 0.8) + 0.5 * partial(hit_t, E1 * 2, 1.0, 0.01, 0.002)
                         + 0.3 * partial(hit_t, E1 * 3, 0.8, 0.01, 0.003) + 0.4 * thump(hit_t)))
    tail = hall(st(hit), 1.4, 0.4)
    rev = hall(st(hit[: int(0.6 * SR)]), 0.5, 1.0)[::-1]            # a reversed reverb of the hit itself
    rev = rev[-int(pre * SR):] * (np.linspace(0, 1, int(pre * SR)) ** 2)[:, None]
    x = np.concatenate([rev * 0.6, tail]); return norm(x), pre

def logo_two_tone():
    """A warm deep strike whose ring holds two notes, the second entering a fifth above: 'bong, then glow'."""
    t = t_(3.2)
    strike = sweep(t, 90, E1 * 2, 0.04) * env(t, 0.002, 0.6) + 0.4 * thump(t)
    n1 = partial(t, E1 * 4, 1.4, 0.005, 0.002) + 0.3 * partial(t, E1 * 8, 0.6, 0.005, 0.003)
    t2 = np.maximum(t - 0.32, 0)
    n2 = (t >= 0.32) * (partial(t2, E1 * 6, 1.3, 0.04, 0.002) + 0.25 * partial(t2, E1 * 12, 0.5, 0.04, 0.003))
    x = np.tanh(1.3 * (strike + 0.55 * n1 + 0.5 * n2))
    return norm(hall(st(filt(x, "low", 5000, 2)), 1.6, 0.3))

# ---- the two-tone family: a strike, then a second note; playful, a brand rather than a film ----
E2, B2, E3, Gs3, B3, E4, Gs4, B4 = 82.41, 123.47, 164.81, 207.65, 246.94, 329.63, 415.30, 493.88
def fit(x, total, fade=0.6):
    """End a sound by `total` seconds with a fade, so nothing is cut by the end of the video."""
    n, f = int(total * SR), int(fade * SR); x = x[:n].copy(); x[-f:] *= (np.linspace(1, 0, f) ** 2)[:, None]; return x
def mallet(t, f, d):
    """A marimba-like note: the fundamental and two fast-dying overtones (1 : 3.9 : 9.2)."""
    return partial(t, f, d, 0.002, 0.001) + 0.35 * partial(t, f * 3.9, d * 0.25, 0.001) + 0.12 * partial(t, f * 9.2, d * 0.08, 0.0005)
def glass(t, f, d):
    """A glassy FM bell note: bright at the strike, pure as it rings."""
    mod = 1.8 * np.exp(-t / (d * 0.3)) * np.sin(2 * np.pi * f * 3.5 * t)
    return np.sin(2 * np.pi * f * t + mod) * env(t, 0.002, d)
def later(t, at, fn):
    t2 = np.maximum(t - at, 0); return (t >= at) * fn(t2)
def deep_strike(t, f, d=0.5): return sweep(t, 90, f, 0.04) * env(t, 0.002, d) + 0.4 * thump(t)
def finish(x, total, lp=6000, decay=1.0, mix=0.28):
    return norm(fit(hall(st(filt(np.tanh(1.3 * x), "low", lp, 2)), decay, mix), total))

def tt_original_short():
    """Two-tone as you liked it, with its tail ended by 3 s."""
    return fit(logo_two_tone(), 3.0)
def tt_bright():
    """The same idea an octave and a half up, on mallets: E then B, light and quick, 1.8 s."""
    t = t_(2.4)
    x = mallet(t, E3, 0.9) + 0.9 * later(t, 0.16, lambda u: mallet(u, B3, 1.0)) + 0.35 * deep_strike(t, E2, 0.25)
    return finish(x, 1.8, 7000, 0.7, 0.25)
def tt_happy():
    """A major third instead of a fifth (E then G#): sunnier, more 'hello'."""
    t = t_(2.8)
    x = deep_strike(t, E2, 0.45) + 0.6 * partial(t, E3, 1.0, 0.004, 0.002) + 0.55 * later(t, 0.24, lambda u: partial(u, Gs3, 1.1, 0.01, 0.002) + 0.3 * glass(u, Gs4, 0.6))
    return finish(x, 2.4)
def tt_glass():
    """The deep strike of the original with a glassy bell as the second note: serious start, playful answer."""
    t = t_(2.8)
    x = deep_strike(t, E2, 0.55) + 0.45 * partial(t, E3, 0.9, 0.004, 0.002) + 0.6 * later(t, 0.28, lambda u: glass(u, B4, 0.9) + 0.5 * glass(u, E4, 0.7))
    return finish(x, 2.6, 9000)
def tt_answer():
    """Descending and resolving: B then E below it, 'ta-da', the second note landing home."""
    t = t_(2.8)
    x = 0.8 * mallet(t, B3, 0.35) + 0.3 * thump(t, 0.01, 2000) + later(t, 0.17, lambda u: deep_strike(u, E2, 0.5) + 0.8 * partial(u, E3, 1.0, 0.004, 0.002) + 0.3 * mallet(u, E4, 0.6))
    return finish(x, 2.5), 0.17 + 0.003   # anchor: the home note
def tt_bwoop():
    """One note that bends up a fifth into the second: a playful 'bwoop', like the mascot hopping into place."""
    t = t_(2.4)
    f = E3 * (1.5 ** np.clip((t - 0.12) / 0.1, 0, 1) ** 2)   # E3 for 0.12 s, then a quick glide to B3
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + 0.3 * np.sin(2 * ph)) * env(t, 0.003, 0.9) + 0.6 * deep_strike(t, E2, 0.35)
    return finish(x, 2.0, 5000, 0.8, 0.25)
def tt_split():
    """The two notes split across the picture: the low note as the mascot lands, the high one as 'BrAIan' opens."""
    gap = OPENED - LAND
    t = t_(gap + 2.0)
    x = deep_strike(t, E2, 0.5) + 0.55 * partial(t, E3, 1.0, 0.004, 0.002) + 0.75 * later(t, gap, lambda u: partial(u, B3, 1.0, 0.006, 0.002) + 0.35 * glass(u, B4, 0.6))
    return finish(x, gap + 1.6)
def gong_short():
    """The deep gong with its tail ended by 2.2 s, finishing well before the picture fades."""
    return fit(logo_gong(), 2.2, 0.8)

# ---- round 4: shorter two-tone, clearer ta-das, gongs that decay on their own ----
def natural(x, safety=4.35):
    """Only a safety trim, far after the sound has died away: no audible fade or cut."""
    return fit(x, safety, 0.5)
def two_tone_short():
    """Two-tone with every decay about 40 % shorter and a smaller hall: the same sound in about 1.8 s."""
    t = t_(2.6)
    strike = sweep(t, 90, E1 * 2, 0.04) * env(t, 0.002, 0.22) + 0.4 * thump(t)
    n1 = partial(t, E1 * 4, 0.36, 0.005, 0.002) + 0.3 * partial(t, E1 * 8, 0.18, 0.005, 0.003)
    n2 = later(t, 0.32, lambda u: partial(u, E1 * 6, 0.33, 0.04, 0.002) + 0.25 * partial(u, E1 * 12, 0.15, 0.04, 0.003))
    x = np.tanh(1.3 * (strike + 0.55 * n1 + 0.5 * n2))
    return norm(natural(hall(st(filt(x, "low", 5000, 2)), 0.28, 0.25)))

def epiano(t, f, d):
    """An electric-piano note: a soft FM body and a short bright tine, clear and round."""
    body = np.sin(2 * np.pi * f * t + 0.9 * np.exp(-t / 0.4) * np.sin(2 * np.pi * f * t))
    tine = np.sin(2 * np.pi * f * 14 * t) * np.exp(-t / 0.012)
    return (body + 0.25 * tine) * env(t, 0.002, d)
def celesta(t, f, d):
    """A clean bell/celesta note: near-harmonic partials that die faster the higher they are."""
    return sum(g * partial(t, f * r, d * k, 0.001) for r, g, k in [(1, 1.0, 1.0), (2.0, 0.5, 0.55), (3.0, 0.22, 0.35), (4.2, 0.12, 0.2)])
def pluck(t, f, d):
    """A synth pluck: two detuned saws through a filter that snaps shut, clear and punchy."""
    saw = lambda g: 2 * ((g * t) % 1) - 1
    raw = (saw(f * 1.004) + saw(f * 0.996) + 0.5 * saw(f * 2)) / 2.5
    out = np.zeros(len(t)); seg = 480
    for i in range(0, len(t), seg):
        c = 600 + 5000 * np.exp(-(i / SR) / 0.07)
        out[i:i + seg] = filt(raw[max(0, i - 3000):i + seg], "low", c, 2)[-len(out[i:i + seg]):]
    return out * env(t, 0.002, d)
def ta_da(voice, hi, lo, gap=0.16, d_hi=0.14, d_lo=0.32, low_support=0.25, room_mix=0.22):
    t = t_(gap + 2.6)
    x = 0.75 * voice(t, hi, d_hi) + later(t, gap, lambda u: voice(u, lo, d_lo) + low_support * sweep(u, 70, E2 / 2 * 2, 0.04) * env(u, 0.002, 0.3))
    return norm(natural(hall(st(np.tanh(1.2 * x)), 0.26, room_mix))), gap + 0.003

def gong_natural(damp=1.0, f0=55.0, bright=4500):
    """The gong rebuilt with short natural decays (about 2 s to silence), so it ends by itself."""
    t = t_(3.2)
    metal = sum(g * partial(t, f0 * r, d * damp, 0.003, 0.0015 * (k + 1)) for k, (r, g, d) in enumerate(
        [(1.0, 1.0, 0.46), (2.32, 0.55, 0.34), (3.01, 0.3, 0.26), (4.25, 0.25, 0.2), (5.39, 0.15, 0.15), (6.63, 0.1, 0.11)]))
    sub = sweep(t, 80, E1, 0.06) * env(t, 0.003, 0.3 * damp)
    x = np.tanh(1.3 * (0.8 * metal + sub + 0.45 * thump(t, 0.015, 2500)))
    return norm(natural(hall(st(filt(x, "low", bright, 2)), 0.32 * damp, 0.22)))

# ---- round 5 ----
def current_rounded(hold=1.0, gone=2.05):
    """The current hit untouched for `hold` s, then an exponential fade reaching -40 dB at `gone` s,
    where the file used to stop: same sound and length, but it dies away instead of stopping dead."""
    x = ownsfx("impact-bass-1").copy()
    t = np.arange(len(x)) / SR
    tau = (gone - hold) / np.log(100)
    x *= np.where(t < hold, 1.0, np.exp(-(t - hold) / tau))[:, None]
    return x

def two_tone_room():
    """Two-tone with a short strike and first note, but a second note that takes its time to fade (~2.8 s)."""
    t = t_(3.6)
    strike = sweep(t, 90, E1 * 2, 0.04) * env(t, 0.002, 0.22) + 0.4 * thump(t)
    n1 = partial(t, E1 * 4, 0.36, 0.005, 0.002) + 0.3 * partial(t, E1 * 8, 0.18, 0.005, 0.003)
    n2 = later(t, 0.32, lambda u: partial(u, E1 * 6, 0.58, 0.04, 0.002) + 0.22 * partial(u, E1 * 12, 0.26, 0.04, 0.003))
    x = np.tanh(1.2 * (strike + 0.55 * n1 + 0.6 * n2))
    return norm(natural(hall(st(filt(x, "low", 5000, 2)), 0.4, 0.25)))

def epiano_clean(t, f, d):
    """A cleaner electric piano: a gentle FM body that settles to a near-pure tone, and only a hint of tine."""
    body = np.sin(2 * np.pi * f * t + 0.35 * np.exp(-t / 0.25) * np.sin(2 * np.pi * f * t))
    tine = np.sin(2 * np.pi * f * 14 * t) * np.exp(-t / 0.008)
    return (body + 0.07 * tine + 0.12 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / (d * 0.5))) * env(t, 0.003, d)
def rise(lo, hi, gap=0.16):
    """Going up: the low note just before the landing, the high note on it, both ringing clean (~2.2 s)."""
    t = t_(gap + 3.2)
    x = 0.8 * epiano_clean(t, lo, 0.32) + later(t, gap, lambda u: epiano_clean(u, hi, 0.5) + 0.08 * np.sin(2 * np.pi * E2 * u) * env(u, 0.004, 0.3))
    return norm(natural(hall(st(x), 0.38, 0.24))), gap + 0.004

# ---- round 6: new single-sound ideas near what was liked (clean and rising, a natural long ring, weight) ----
E5 = 659.26
def tau(to_minus40): return to_minus40 / 4.6          # an exponential decay that is 40 dB down at `to_minus40` s
def strum():
    """A quick rising E-B-E on the clean electric piano, the top E landing with the mascot."""
    gaps = [0.0, 0.075, 0.15]; t = t_(3.6)
    x = sum(later(t, g, lambda u, f=f: epiano_clean(u, f, tau(2.0 if f == E4 else 1.2))) * (0.7 if f != E4 else 1.0)
            for g, f in zip(gaps, [E3, B3, E4]))
    return norm(natural(hall(st(x), 0.38, 0.24))), 0.15 + 0.004
def kalimba(t, f, d):
    """A thumb-piano tine: a warm fundamental, an inharmonic overtone that dies fast, a soft pluck."""
    return (partial(t, f, d, 0.0015) + 0.3 * partial(t, f * 5.95, d * 0.12, 0.0008)
            + 0.12 * filt(rng.standard_normal(len(t)), "band", [f * 2, f * 8]) * env(t, 0.0003, 0.006))
def kalimba_octave():
    """The octave-up idea on a kalimba: E, then the E above with the mascot. Warm, wooden, playful."""
    t = t_(3.4)
    x = 0.75 * kalimba(t, E4, tau(1.0)) + later(t, 0.16, lambda u: kalimba(u, E5, tau(2.0)))
    return norm(natural(hall(st(x), 0.32, 0.22))), 0.16 + 0.003
def vibraphone():
    """One soft vibraphone chord (E, B, E above) struck as the mascot lands, its motor tremolo slowing as it rings."""
    t = t_(4.0)
    trem = 1 + 0.35 * np.sin(2 * np.pi * (5.5 * t - 0.8 * t ** 2 / 2).clip(0, None)) * np.exp(-t / 2.5)
    bar = lambda f, g: g * (partial(t, f, tau(2.8), 0.002) + 0.25 * partial(t, f * 3.98, tau(0.5), 0.001) + 0.08 * partial(t, f * 9.2, tau(0.15), 0.0005))
    x = (bar(E3, 0.8) + bar(B3, 0.6) + bar(E4, 0.7)) * trem
    return norm(natural(hall(st(x), 0.45, 0.25)))
def singing_bowl():
    """A struck singing bowl: the gong's long natural ring, but pure and calm, its partials slowly beating."""
    t = t_(4.0); f0 = 164.81
    x = sum(g * partial(t, f0 * r, tau(d), 0.004, 0.0008 * (k + 1)) for k, (r, g, d) in enumerate([(1, 1.0, 3.0), (2.71, 0.45, 2.0), (5.12, 0.2, 1.2), (8.21, 0.08, 0.6)]))
    x += 0.25 * thump(t, 0.004, 3000)
    return norm(natural(hall(st(x), 0.4, 0.2)))
def felt_piano():
    """A low E on a felt-muted piano with a little sub under it: the current hit's weight, but a note."""
    t = t_(4.0)
    x = sum((0.85 ** (n - 1)) * partial(t, E1 * n * np.sqrt(1 + 0.0004 * n * n), tau(3.0 / (1 + 0.35 * (n - 1))), 0.004) for n in range(1, 12))
    x = filt(x, "low", 1800, 2) + 0.5 * sweep(t, 70, E1, 0.05) * env(t, 0.003, tau(1.2)) + 0.3 * thump(t, 0.01, 600)
    return norm(natural(hall(st(np.tanh(1.2 * x)), 0.45, 0.22)))
def octave_weight():
    """The clean electric-piano octave up, with a deep sub boom under the landing note: clarity with weight."""
    t = t_(3.8); g = 0.16
    x = 0.8 * epiano_clean(t, E3, 0.32) + later(t, g, lambda u: epiano_clean(u, E4, 0.5) + 0.9 * sweep(u, 85, E1, 0.05) * env(u, 0.003, tau(1.6)))
    return norm(natural(hall(st(np.tanh(1.1 * x)), 0.38, 0.24))), g + 0.004

# ---- round 7: around the four favourites (current's weight, the clean e-piano octave, the gong's ring, the vibraphone chord) ----
Fs4 = 369.99
def vib_bar(t, f, ring=2.8):
    """One vibraphone bar: fundamental, the 4th partial and a faint 10th, each dying faster than the last."""
    return partial(t, f, tau(ring), 0.002) + 0.25 * partial(t, f * 3.98, tau(0.5), 0.001) + 0.08 * partial(t, f * 9.2, tau(0.15), 0.0005)
def vib_trem(t, rate=5.5, depth=0.35, fade=2.5):
    return 1 + depth * np.sin(2 * np.pi * (rate * t - 0.8 * t ** 2 / 2).clip(0, None)) * np.exp(-t / fade)
def vib_chord(notes, ring=2.8, depth=0.35, extra=None):
    t = t_(4.0)
    x = sum(g * vib_bar(t, f, ring) for f, g in notes) * vib_trem(t, depth=depth)
    if extra is not None: x = x + extra(t)
    return norm(natural(hall(st(x), 0.45, 0.25)))

def vib_octave():
    """The vibraphone playing the octave-up figure you liked on the electric piano: E, then the E above."""
    t = t_(4.0); g = 0.16
    x = 0.75 * vib_bar(t, E3, 1.4) * vib_trem(t) + later(t, g, lambda u: vib_bar(u, E4, 2.6) * vib_trem(u))
    return norm(natural(hall(st(x), 0.45, 0.25))), g + 0.003
def epiano_chord():
    """The clean electric piano striking the vibraphone's E-B-E chord all at once: soft, round, ~2.4 s."""
    t = t_(4.0)
    x = 0.8 * epiano_clean(t, E3, tau(2.4)) + 0.6 * epiano_clean(t, B3, tau(2.2)) + 0.7 * epiano_clean(t, E4, tau(2.4))
    return norm(natural(hall(st(x), 0.4, 0.24)))
def tongue_drum():
    """A steel tongue drum (handpan-like) striking E and the E above together: warm metal, clean ring."""
    t = t_(4.0)
    note = lambda f, g, ring: g * (partial(t, f, tau(ring), 0.003, 0.001) + 0.4 * partial(t, f * 2.0, tau(ring * 0.55), 0.003, 0.0015)
                                  + 0.15 * partial(t, f * 3.01, tau(ring * 0.3), 0.002))
    x = note(E3, 0.9, 2.6) + note(E4, 0.6, 2.2) + 0.25 * thump(t, 0.006, 1200)
    return norm(natural(hall(st(np.tanh(1.1 * x)), 0.45, 0.25)))

# ---- round 8: the vibraphone with a clean, intentional weight ----
def weight(n, ring=1.6, octave=0.45, sat=1.0, click=0.08):
    """A clean pitched sub on E1: it glides down from ~62 Hz into E within ~50 ms (punch, then a note),
    with an E2 octave so small speakers hear it, optional saturation for fullness (its 3rd harmonic is B2,
    in the chord), a tiny soft click for definition. Mono and dry: it never goes through the reverb."""
    t = np.arange(n) / SR
    f = E1 * (1 + 0.5 * np.exp(-t / 0.025))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + octave * np.sin(2 * ph)) * env(t, 0.003, tau(ring))
    if sat > 1.0: x = np.tanh(sat * x) / np.tanh(sat)
    x += click * filt(rng.standard_normal(n), "low", 1200) * env(t, 0.0003, 0.0025)
    return np.stack([x, x], 1)
def vib_with_weight(gain, notes=((E3, 0.8), (B3, 0.6), (E4, 0.7)), **kw):
    t = t_(4.0)
    chord = sum(g * vib_bar(t, f) for f, g in notes) * vib_trem(t)
    wet = hall(st(chord), 0.45, 0.25)
    wet = wet / np.abs(wet).max()
    w = weight(len(wet), **kw)
    return norm(natural(wet + gain * w / np.abs(w).max()))
def vib_octave_with_weight(gain, **kw):
    t = t_(4.0); g = 0.16
    x = 0.75 * vib_bar(t, E3, 1.4) * vib_trem(t) + later(t, g, lambda u: vib_bar(u, E4, 2.6) * vib_trem(u))
    wet = hall(st(x), 0.45, 0.25); wet = wet / np.abs(wet).max()
    w = np.zeros_like(wet); i = int(g * SR); w[i:] = weight(len(wet) - i, **kw)
    return norm(natural(wet + gain * w / np.abs(w).max())), g + 0.003

# ---- round 9: 'full weight' with the weight fading in step with the chord ----
def smooth_env(x, win=0.3):
    """The chord's loudness over time, smoothed over `win` s so the tremolo's wobble is not copied."""
    m = np.abs(x).max(1); w = int(win * SR)
    e = np.sqrt(np.convolve(m ** 2, np.ones(w) / w, "same")); return e / e.max()
def weight_following(n, follow, octave=0.5, sat=1.8, click=0.08, stretch=1.0, steep=1.0):
    """The same pitched E sub as 'full weight', but its loudness follows the chord's (optionally a bit
    slower: `stretch` > 1 holds it longer), so the two fade as one."""
    t = np.arange(n) / SR
    f = E1 * (1 + 0.5 * np.exp(-t / 0.025)); ph = 2 * np.pi * np.cumsum(f) / SR
    e = np.interp(t / stretch, t, follow) ** steep   # steeper before saturation, which flattens the fade
    peak = np.argmax(follow)                       # before the chord's peak, use the sub's own fast attack
    e[: peak] = np.maximum(e[: peak], np.minimum(t[: peak] / 0.003, 1.0))
    tone = np.sin(ph) + octave * np.sin(2 * ph)
    if sat > 1.0: tone = np.tanh(sat * tone) / np.tanh(sat)   # saturate at full level: a constant, full timbre
    x = tone * e                                               # then the chord's fade, which stays exact
    x += click * filt(rng.standard_normal(n), "low", 1200) * env(t, 0.0003, 0.0025)
    return np.stack([x, x], 1)
def vib_full_synced(gain=0.95, stretch=1.0, steep=1.0):
    t = t_(4.0)
    chord = sum(g * vib_bar(t, f) for f, g in ((E3, 0.8), (B3, 0.6), (E4, 0.7))) * vib_trem(t)
    wet = hall(st(chord), 0.45, 0.25); wet = wet / np.abs(wet).max()
    w = weight_following(len(wet), smooth_env(wet), stretch=stretch, steep=steep)
    return norm(natural(wet + gain * w / np.abs(w).max()))

SETS = {
    "0-current": ("Current", "The old intro sound, kept as the loudness reference.", [whoosh_in, (ownsfx("impact-bass-1"), LAND, -6)]),
    # the opening asset comes first: made with the noise generator fresh, it is identical to kept/24-full-synced.wav
    "24-full-synced": ("Vibraphone + full weight, in step (the opening asset)", "", [(vib_full_synced(steep=1.1), LAND, 0)]),
    "4-epiano-octave-up": ("Electric piano, up an octave", "", [(*rise(E3, E4)[:1], LAND, 0, rise(E3, E4)[1])]),
    "9-vibraphone": ("Vibraphone chord", "", [(vibraphone(), LAND, 0)]),
    "13-vib-octave": ("Vibraphone octave", "", [(*vib_octave()[:1], LAND, 0, vib_octave()[1])]),
}

import json, os
os.makedirs(f"{intro}/sound-sets/stems", exist_ok=True)
meta = {}
for key, (name, desc, events) in SETS.items():
    mix = np.zeros((int((DUR + 3) * SR), 2))
    for ev in events:
        x, at, g = ev[:3]
        i = int(round(at * SR)) - (int(ev[3] * SR) if len(ev) > 3 else attack(x))
        if i < 0: x, i = x[-i:], 0           # a long lead-in (cinematic whoosh) is trimmed to start at 0
        mix[i:i + len(x)] += x[: len(mix) - i] * db(g)
    mix = mix[: int(DUR * SR)]
    n = int(0.15 * SR); mix[-n:] *= np.linspace(1, 0, n)[:, None]
    wavfile.write(f"{intro}/sound-sets/stems/{key}.wav", SR, mix.astype(np.float32))
    meta[key] = {"name": name, "desc": desc}
json.dump(meta, open(f"{intro}/sound-sets/stems/sets.json", "w"), indent=1)
print("\n".join(f"{k}: peak {20*np.log10(np.abs(wavfile.read(f'{intro}/sound-sets/stems/{k}.wav')[1]).max()):.1f} dBFS" for k in SETS))
