"""Make the outro's layout proposals from compositions/card.html.

usage:  python3 proposals/make_proposals.py [--render [name ...]]        (from assets/outro)

Each proposal keeps the intro part of the scene exactly (0-3.3 s: the lockup, the name, the punch line) and
replaces only what comes after (starting from proposals/base-card.html): the links' styles, their markup and their timeline. It writes
compositions/proposals/<name>.html. With --render it also checks, snapshots and renders every proposal to
proposals/<name>.mp4, each from a temporary copy of the project whose index.html mounts that scene (a project
keeps a single root index.html). Proposal 1 (p1-column) is proposals/base-card.html, the column layout the outro first had. Proposal 6
(p6-side) was chosen: compositions/card.html is a copy of compositions/proposals/p6-side.html.
"""
import os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
base = (HERE / "proposals/base-card.html").read_text()   # the outro's scene before proposal 6 replaced it
root = (HERE / "index.html").read_text()

STYLE_START = "      /* The outro's links: a centred column under the risen lockup. */"
STYLE_END = "    </style>"
MARKUP_START = '      <div id="card-links">'
MARKUP_END = "    </div>\n\n    <script>"
TL_START = "      // 3.3–3.95  the outro:"
TL_END = "      window.__timelines[\"card\"] = tl;"


def cut(s, a, b):
    i, j = s.index(a), s.index(b, s.index(a))
    return s[:i], s[j:]


# shared bits of script: read the variables, and type any line into a typed/rest pair
VARS = '''      const v = window.__hyperframes?.getVariables?.() || {};
      const url = v.url || "getbraian.github.io";
      const cmd = v.command || "npx braian";
      const handle = v.handle || "@thepeg";
      // types `text` into #<id>-typed, keeping the untyped rest in #<id>-rest (hidden, so the width never changes)
      const typeInto = (id, text, at, perChar) => {
        const typed = document.querySelector("#" + id + "-typed"), rest = document.querySelector("#" + id + "-rest");
        const p = { n: 0 };
        const show = () => { const n = Math.round(p.n); typed.textContent = text.slice(0, n); rest.textContent = text.slice(n); };
        show();
        tl.fromTo(p, { n: 0 }, { n: text.length, duration: text.length * perChar, ease: "none", onUpdate: show, immediateRender: false }, at);
      };
'''
FADE = """
      // the final composition holds to the end: no fade

"""
RISE = '      tl.to("#card-stack", { y: -190, scale: 0.78, duration: 0.65, ease: "power3.inOut" }, 3.3);\n'
SLIDE_IN = '{ opacity: 0, y: 24, filter: "blur(6px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.35, ease: "power3.out" }'
TYPED_CSS = '''      .hidden-rest {
        visibility: hidden;
      }
      .block-caret {
        display: inline-block;
        position: relative;
        width: 0;
        height: 1em;
        vertical-align: -0.12em;
      }
      .block-caret::after {
        content: "";
        position: absolute;
        left: 3px;
        top: 0;
        width: 0.55em;
        height: 100%;
        background: var(--accent);
        opacity: 0.85;
      }
'''


GLOBE = '<svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>'
XLOGO = '<svg class="card-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"/></svg>'
ICON_CSS = '''      .card-icon {
        width: 0.8em;
        height: 0.8em;
        flex: none;
        color: var(--accent);
      }
'''


def typed(id_, var, text):
    return f'<span id="{id_}-typed"></span><span class="block-caret" id="{id_}-caret"></span><span class="hidden-rest" id="{id_}-rest" data-var-text="{var}">{text}</span>'


PROPOSALS = {
    # 2: the command is the hero; the website and the handle share one quieter line under it
    "p2-command-hero": (
        TYPED_CSS + '''''' + ICON_CSS + '''      /* The command is the hero; the website and the handle share one line under it. */
      #card-links {
        position: absolute;
        left: 0;
        right: 0;
        top: 600px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 34px;
      }
      #card-cmd {
        display: flex;
        align-items: center;
        gap: 28px;
        padding: 22px 44px 22px 38px;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.16);
        font-family: "JetBrains Mono", monospace;
        font-size: 66px;
        line-height: 1.2;
        color: var(--ink);
        white-space: nowrap;
      }
      #card-prompt {
        color: var(--accent);
      }
      #card-meta {
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 0;
        color: var(--muted);
        font-size: 40px;
        line-height: 1.2;
      }
      #card-meta b {
        color: var(--ink);
        font-weight: 700;
      }
      #card-dot {
        margin: 0 0.5em;
        color: var(--accent);
      }
''',
        '''      <div id="card-links">
        <div id="card-cmd"><span id="card-prompt">$</span><span>''' + typed("card-cmd", "command", "npx braian") + '''</span></div>
        <p id="card-meta">''' + GLOBE + '''<b data-var-text="url">getbraian.github.io</b><span id="card-dot">·</span>''' + XLOGO + '''<b data-var-text="handle">@thepeg</b></p>
      </div>
''',
        RISE + '''      tl.fromTo("#card-cmd", { opacity: 0, y: 24, scale: 0.96 }, { opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "power3.out" }, 3.75);
      typeInto("card-cmd", cmd, 3.95, 0.05);
      tl.fromTo("#card-meta", ''' + SLIDE_IN + ''', 4.6);
''',
    ),
    # 3: three cards side by side, each with a small label
    "p3-cards": (
        TYPED_CSS + '''''' + ICON_CSS + '''      /* Three cards side by side under the lockup, each with a small label. */
      .card-iconed {
        display: flex;
        align-items: center;
        gap: 14px;
      }
      #card-links {
        position: absolute;
        left: 0;
        right: 0;
        top: 640px;
        display: flex;
        justify-content: center;
        gap: 28px;
      }
      .card-box {
        width: 470px;
        padding: 30px 34px 34px;
        border-radius: 22px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.13);
        display: flex;
        flex-direction: column;
        gap: 14px;
      }
      .card-label {
        margin: 0;
        color: var(--accent);
        font-size: 28px;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
      }
      .card-value {
        margin: 0;
        color: var(--ink);
        font-size: 38px;
        font-weight: 700;
        line-height: 1.2;
        white-space: nowrap;
      }
      .card-mono {
        font-family: "JetBrains Mono", monospace;
        font-weight: 400;
      }
      #card-prompt {
        color: var(--accent);
        margin-right: 0.5em;
      }
''',
        '''      <div id="card-links">
        <div class="card-box" id="card-box-2"><p class="card-label">Try it</p><p class="card-value card-mono"><span id="card-prompt">$</span>''' + typed("card-cmd", "command", "npx braian") + '''</p></div>
        <div class="card-box" id="card-box-1"><p class="card-label">Website</p><p class="card-value card-iconed">''' + GLOBE + '''<span data-var-text="url">getbraian.github.io</span></p></div>
        <div class="card-box" id="card-box-3"><p class="card-label">Follow on X</p><p class="card-value card-iconed">''' + XLOGO + '''<span data-var-text="handle">@thepeg</span></p></div>
      </div>
''',
        RISE + '''      tl.fromTo("#card-box-2", ''' + SLIDE_IN + ''', 3.75);
      typeInto("card-cmd", cmd, 3.95, 0.045);
      tl.fromTo("#card-box-1", ''' + SLIDE_IN + ''', 4.5);
      tl.fromTo("#card-box-3", ''' + SLIDE_IN + ''', 4.7);
''',
    ),
    # 4: a terminal window that types all three lines, like a README in a shell
    "p4-terminal": (
        TYPED_CSS + '''      /* A terminal window under the lockup that types all three lines. */
      #card-links {
        position: absolute;
        left: 0;
        right: 0;
        top: 585px;
        display: flex;
        justify-content: center;
      }
      #card-term {
        width: 860px;
        border-radius: 20px;
        background: rgba(8, 12, 28, 0.72);
        border: 1px solid rgba(255, 255, 255, 0.14);
        overflow: hidden;
      }
      #card-term-bar {
        display: flex;
        gap: 12px;
        padding: 18px 22px;
        background: rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      }
      .card-term-dot {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.22);
      }
      #card-term-body {
        padding: 26px 38px 32px;
        display: flex;
        flex-direction: column;
        gap: 14px;
        font-family: "JetBrains Mono", monospace;
        font-size: 38px;
        line-height: 1.25;
        white-space: nowrap;
      }
      .card-term-line {
        margin: 0;
        color: var(--ink);
      }
      .card-term-comment {
        color: var(--muted);
      }
      .card-term-sign {
        color: var(--accent);
        margin-right: 0.6em;
      }
      .card-term-line .block-caret::after {
        opacity: 0;
      }
      #card-l2 .block-caret::after {
        opacity: 0.85;
      }
''',
        '''      <div id="card-links">
        <div id="card-term">
          <div id="card-term-bar"><span class="card-term-dot"></span><span class="card-term-dot"></span><span class="card-term-dot"></span></div>
          <div id="card-term-body">
            <p class="card-term-line" id="card-l2"><span class="card-term-sign">$</span>''' + typed("card-cmd", "command", "npx braian") + '''</p>
            <p class="card-term-line card-term-comment" id="card-l1"><span class="card-term-sign">#</span>''' + typed("card-url", "url", "getbraian.github.io") + '''</p>
            <p class="card-term-line card-term-comment" id="card-l3"><span class="card-term-sign">#</span>''' + typed("card-handle", "handle", "@thepeg") + ''' on X</p>
          </div>
        </div>
      </div>
''',
        RISE + '''      tl.fromTo("#card-term", { opacity: 0, y: 30, scale: 0.97 }, { opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "power3.out" }, 3.7);
      typeInto("card-cmd", cmd, 4.0, 0.05);
      typeInto("card-url", url, 4.65, 0.03);
      typeInto("card-handle", handle, 5.45, 0.04);
''',
    ),
    # 6: side by side, refined: the command first, then the website and the handle, each with its icon
    "p6-side": (
        TYPED_CSS + '''      /* The lockup moves left; to its right, past a thin accent divider: the command, the website, the handle. */
      #card-divider {
        position: absolute;
        left: 1043px;
        top: 400px;
        width: 2px;
        height: 280px;
        background: var(--accent);
        opacity: 0;
        transform-origin: center top;
      }
      #card-links {
        position: absolute;
        top: 0;
        bottom: 0;
        left: 1087px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;
        gap: 26px;
      }
      #card-cmd {
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 12px 44px 12px 22px;
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.14);
        font-family: "JetBrains Mono", monospace;
        font-size: 44px;
        line-height: 1.2;
        color: var(--ink);
        white-space: nowrap;
      }
      #card-prompt {
        color: var(--accent);
      }
      /* The website and the handle: an icon in the accent colour, lined up under the prompt's "$", then the text. */
      .card-link {
        display: flex;
        align-items: center;
        gap: 18px;
        margin: 0;
        padding-left: 17px;
        color: var(--ink);
        font-size: 44px;
        font-weight: 700;
        letter-spacing: -0.01em;
        line-height: 1.2;
        white-space: nowrap;
      }
      /* The cursor: a thin accent bar a little apart from the last letter, all the way: it follows the letters
         as the command types, then blinks until the end (--bar). The shared block cursor is turned off. */
      #card-cmd-caret {
        --block: 0;
        --bar: 0.9;
      }
      #card-cmd-caret::after {
        opacity: var(--block);
      }
      #card-cmd-caret::before {
        content: "";
        position: absolute;
        left: 0.38em;
        top: 0.04em;
        width: 3px;
        height: 0.95em;
        border-radius: 2px;
        background: var(--accent);
        opacity: var(--bar);
      }
      .card-icon {
        width: 36px;
        height: 36px;
        flex: none;
        color: var(--accent);
      }
''',
        '''      <div id="card-divider"></div>
      <div id="card-links">
        <div id="card-cmd"><span id="card-prompt">$</span><span>''' + typed("card-cmd", "command", "npx braian") + '''</span></div>
        <p class="card-link" id="card-url">''' + GLOBE + '''<span data-var-text="url">getbraian.github.io</span></p>
        <p class="card-link" id="card-handle">''' + XLOGO + '''<span data-var-text="handle">@thepeg</span></p>
      </div>
''',
        '''      tl.to("#card-stack", { x: -275, scale: 0.7, duration: 0.7, ease: "power3.inOut" }, 3.3);
      tl.fromTo("#card-divider", { opacity: 0, scaleY: 0 }, { opacity: 0.8, scaleY: 1, duration: 0.45, ease: "power3.out" }, 3.75);
      tl.fromTo("#card-cmd", { opacity: 0, x: -24 }, { opacity: 1, x: 0, duration: 0.35, ease: "power3.out" }, 3.95);
      typeInto("card-cmd", cmd, 4.15, 0.045);
      // once typed, the thin bar blinks (about 0.53 s on, 0.53 s off, soft 80 ms edges) to the end
      const typedAt = 4.15 + cmd.length * 0.045 + 0.12;
      for (let t = typedAt + 0.53, on = false; t < 9; t += 0.53, on = !on) {
        tl.to("#card-cmd-caret", { "--bar": on ? 0.9 : 0, duration: 0.08, ease: "none" }, t);
      }
      tl.fromTo("#card-url", { opacity: 0, x: -24, filter: "blur(6px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 0.35, ease: "power3.out" }, 4.7);
      tl.fromTo("#card-handle", { opacity: 0, x: -24, filter: "blur(6px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: 0.35, ease: "power3.out" }, 4.95);
''',
    ),
}

(HERE / "compositions/proposals").mkdir(exist_ok=True)
(HERE / "compositions/proposals/p1-column.html").write_text(base)   # proposal 1 is the base itself
for name, (css, markup, timeline) in PROPOSALS.items():
    s = base
    head, tail = cut(s, STYLE_START, STYLE_END); s = head + css + tail
    head, tail = cut(s, MARKUP_START, MARKUP_END); s = head + markup + tail
    head, tail = cut(s, TL_START, TL_END)
    FADE_ = FADE
    s = head + VARS + "\n      // 3.3 on  the outro: " + name + "\n" + timeline + FADE_ + tail
    (HERE / f"compositions/proposals/{name}.html").write_text(s)
    print("wrote", name)

if "--render" in sys.argv:
    # A project has one root index.html, so each proposal renders from a temporary copy of the project whose
    # index.html mounts that proposal's scene; proposal 1 is the project itself.
    env = dict(os.environ, HYPERFRAMES_NO_TELEMETRY="1")
    CLI = ["npx", "--yes", "hyperframes@0.9.41"]
    jobs = [("p1-column", "p1-column")] + [(n, n) for n in PROPOSALS]
    only = [x for x in sys.argv[1:] if not x.startswith("--")]   # optional: names of the proposals to render
    jobs = [j for j in jobs if not only or j[0] in only]
    for name, scene in jobs:
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "outro"
            top_only = {"renders", "proposals", ".hyperframes", ".thumbnails", ".waveform-cache"}   # not compositions/proposals
            shutil.copytree(HERE, proj, ignore=lambda d, names: [n for n in names if (Path(d) == HERE and n in top_only) or n.endswith(".mp4")])
            if scene:
                (proj / "index.html").write_text(root.replace('data-composition-src="compositions/card.html"', f'data-composition-src="compositions/proposals/{scene}.html"'))
            check = subprocess.run(CLI + ["check"], cwd=proj, env=env, capture_output=True, text=True).stdout
            problems = [l for l in check.splitlines() if "✗" in l or ("⚠" in l and "first_frame_empty" not in l)]
            print(name, "check:", "passed" if not problems else "\n  " + "\n  ".join(problems))
            subprocess.run(CLI + ["snapshot", "--at", "4.3,5.0,8.9", "--no-end", "-o", str(HERE / "proposals/snapshots" / name)], cwd=proj, env=env, capture_output=True)
            subprocess.run(CLI + ["render", "--quality", "delivery", "-o", str(HERE / f"proposals/{name}.mp4")], cwd=proj, env=env, capture_output=True, check=True)
            print(name, "rendered")
