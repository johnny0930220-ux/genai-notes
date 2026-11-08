#!/usr/bin/env python3
"""把 content/ 裡的 Markdown 筆記轉成網站。

用法：
    python3 build.py           檢查格式，沒問題就產生網站
    python3 build.py --check   只檢查格式，不產生檔案

只用 Python 標準庫，不需要安裝任何套件。
規則說明請看 AGENTS.md。
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WEEKS_DIR = ROOT / "content" / "weeks"
PAGES_DIR = ROOT / "content" / "pages"
TEMPLATE = ROOT / "templates" / "page.html"
OUT_NOTES = ROOT / "notes"

SITE_TITLE = "生成式 AI 課程筆記"
REQUIRED_META = ["week", "title", "slides", "summary", "keywords", "related"]
REQUIRED_SECTIONS = ["課堂重點", "重要名詞", "本週作業", "和其他週的關係", "延伸思考"]
WEEK_FILE_RE = re.compile(r"^w(\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
PAGE_FILE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
CITE_RE = re.compile(r"（p\.\d+(?:[–-]\d+)?(?:、p\.\d+(?:[–-]\d+)?)*）")
FORBIDDEN = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "不可以放 email"),
    (re.compile(r"(?<!\d)\d{9}(?!\d)"), "不可以放學號或九碼數字（可能是個資）"),
    (re.compile(r"(?<!\d)09\d{2}-?\d{3}-?\d{3}(?!\d)"), "不可以放手機號碼"),
    (re.compile(r"^\s*\|.*\|\s*$", re.M), "不使用表格，請改成條列"),
    (re.compile(r"<table", re.I), "不使用表格，請改成條列"),
]


# ---------------------------------------------------------------- 解析

def parse_front_matter(text, path):
    if not text.startswith("---\n"):
        raise ValueError(f"{path.name}: 檔案開頭必須是 --- 開始的 front matter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{path.name}: front matter 缺少結尾的 ---")
    meta = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"{path.name}: front matter 這行看不懂：{line}")
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            value = [v.strip() for v in value[1:-1].split(",") if v.strip()]
        meta[key] = value
    return meta, text[end + 5:]


def slugify(text):
    s = re.sub(r"[^\w一-鿿-]+", "-", text.strip().lower())
    return s.strip("-") or "section"


def inline(text):
    """處理行內語法：數學式、程式碼、粗體、連結。"""
    keep = []

    def stash(s):
        keep.append(s)
        return f"\x00{len(keep) - 1}\x00"

    text = re.sub(r"`([^`]+)`", lambda m: stash(f"<code>{html.escape(m.group(1))}</code>"), text)
    text = re.sub(r"\$([^$\n]+)\$", lambda m: stash(f'<span class="math">\\({html.escape(m.group(1))}\\)</span>'), text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    def link(m):
        label, url = m.group(1), m.group(2)
        ext = url.startswith("http")
        if url.endswith(".md") and not ext:
            url = url.rsplit("/", 1)[-1][:-3] + ".html"
        attrs = ' target="_blank" rel="noopener"' if ext else ""
        return f'<a href="{url}"{attrs}>{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(r"（(p\.[^）]+)）", r'<span class="cite">\1</span>', text)
    return re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], text)


def markdown_to_html(md):
    """支援 AGENTS.md 列出的 Markdown 子集，回傳 (html, 目錄)。"""
    lines = md.splitlines()
    out, toc = [], []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            lang = line[3:].strip()
            buf = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            cls = f' class="lang-{lang}"' if lang else ""
            out.append(f"<pre><code{cls}>{html.escape(chr(10).join(buf))}</code></pre>")
            continue
        if line.strip().startswith("$$"):
            buf = [line.strip()[2:]]
            if not (line.strip().endswith("$$") and len(line.strip()) > 2):
                i += 1
                while i < len(lines) and "$$" not in lines[i]:
                    buf.append(lines[i])
                    i += 1
                buf.append(lines[i].replace("$$", "") if i < len(lines) else "")
            else:
                buf = [line.strip()[2:-2]]
            i += 1
            out.append(f'<div class="math-block">\\[{html.escape(" ".join(buf).strip())}\\]</div>')
            continue
        m = re.match(r"^(#{2,4})\s+(.*)$", line)
        if m:
            level, title = len(m.group(1)), m.group(2).strip()
            anchor = slugify(title)
            if level <= 3:
                toc.append((level, title, anchor))
            out.append(f'<h{level} id="{anchor}">{inline(title)}</h{level}>')
            i += 1
            continue
        if line.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i][1:].strip())
                i += 1
            out.append(f'<blockquote class="callout"><p>{inline(" ".join(buf))}</p></blockquote>')
            continue
        if re.match(r"^\s*(-|\d+\.)\s+", line):
            ordered = bool(re.match(r"^\s*\d+\.", line))
            tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines) and re.match(r"^\s*(-|\d+\.)\s+", lines[i]):
                item = re.sub(r"^\s*(-|\d+\.)\s+", "", lines[i])
                i += 1
                while i < len(lines) and lines[i].startswith("  ") and lines[i].strip() \
                        and not re.match(r"^\s*(-|\d+\.)\s+", lines[i]):
                    item += " " + lines[i].strip()
                    i += 1
                items.append(f"<li>{inline(item)}</li>")
            out.append(f"<{tag}>{''.join(items)}</{tag}>")
            continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{2,4}\s|```|>|\s*(-|\d+\.)\s+|\s*\$\$)", lines[i]):
            buf.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>")
    return "\n".join(out), toc


# ---------------------------------------------------------------- 檢查

def section_bodies(body):
    parts = re.split(r"^## +(.+)$", body, flags=re.M)
    return [(parts[k].strip(), parts[k + 1]) for k in range(1, len(parts), 2)]


def check_week(path, meta, body, all_ids):
    errs = []
    m = WEEK_FILE_RE.match(path.name)
    if not m:
        errs.append("檔名要像 w04-next-token.md：w + 兩位數週次 + 英文小寫與連字號")
    for key in REQUIRED_META:
        if key not in meta or meta[key] in ("", []):
            errs.append(f"front matter 缺少 {key}")
    if m and str(meta.get("week", "")).strip() != str(int(m.group(1))):
        errs.append(f"week: {meta.get('week')} 和檔名的週次 {int(m.group(1))} 不一致")
    if len(meta.get("summary", "")) > 60:
        errs.append("summary 超過 60 字，請縮短成一句話")
    kws = meta.get("keywords", [])
    if not isinstance(kws, list) or not 3 <= len(kws) <= 8:
        errs.append("keywords 要寫成 [a, b, c]，3～8 個")
    rel = meta.get("related", [])
    if not isinstance(rel, list):
        errs.append("related 要寫成 [w03, w05] 這種清單")
    else:
        for r in rel:
            if r not in all_ids:
                errs.append(f"related 裡的 {r} 找不到對應的筆記")
    titles = [t for t, _ in section_bodies(body)]
    if titles != REQUIRED_SECTIONS:
        errs.append("二級標題（##）必須剛好依序是：" + "、".join(REQUIRED_SECTIONS) + f"；目前是：{'、'.join(titles) or '（沒有）'}")
    for title, text in section_bodies(body):
        if title == "課堂重點":
            subs = re.split(r"^### +(.+)$", text, flags=re.M)
            if len(subs) < 5:
                errs.append("課堂重點底下至少要有 2 個 ### 小節")
            for k in range(1, len(subs), 2):
                if not CITE_RE.search(subs[k + 1]):
                    errs.append(f"小節「{subs[k].strip()}」沒有標投影片頁碼，格式是（p.12）或（p.12–15）")
        if title == "和其他週的關係":
            linked = sorted(set(re.findall(r"\]\((w\d{2})-[^)]*\.md\)", text)))
            if not linked:
                errs.append("和其他週的關係至少要連到一篇其他週的筆記，寫法是 [W03 標題](w03-xxx.md)")
            if isinstance(rel, list):
                for l in linked:
                    if l not in rel:
                        errs.append(f"和其他週的關係連到了 {l}，但 related 沒有列 {l}")
                for r in rel:
                    if r not in linked:
                        errs.append(f"related 有 {r}，但和其他週的關係沒有連到 {r}")
        if title == "重要名詞":
            if not re.search(r"^- \*\*.+?\*\*：", text, re.M):
                errs.append("重要名詞要寫成「- **名詞**：說明」")
    return errs


def check_common(path, text):
    errs = []
    for rx, msg in FORBIDDEN:
        if rx.search(text):
            errs.append(msg)
    if "![" in text:
        for src in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
            if not src.startswith("../assets/img/") or not (ROOT / "assets" / "img" / Path(src).name).exists():
                errs.append(f"圖片 {src} 必須放在 assets/img/ 而且檔案要存在")
    return errs


def load_all():
    weeks, pages, errors = [], [], {}
    week_files = sorted(WEEKS_DIR.glob("*.md"))
    ids = {p.name[:3] for p in week_files}
    seen = {}
    for path in week_files:
        text = path.read_text(encoding="utf-8")
        try:
            meta, body = parse_front_matter(text, path)
        except ValueError as e:
            errors[path.name] = [str(e)]
            continue
        errs = check_week(path, meta, body, ids) + check_common(path, text)
        wk = str(meta.get("week"))
        if wk in seen:
            errs.append(f"week {wk} 和 {seen[wk]} 重複")
        seen[wk] = path.name
        if errs:
            errors[path.name] = errs
        weeks.append({"id": path.name[:3], "file": path.name, "meta": meta, "body": body})
    for path in sorted(PAGES_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        errs = [] if PAGE_FILE_RE.match(path.name) else ["檔名只能用英文小寫、數字和連字號"]
        try:
            meta, body = parse_front_matter(text, path)
            if "title" not in meta:
                errs.append("front matter 缺少 title")
        except ValueError as e:
            errors[path.name] = [str(e)]
            continue
        errs += check_common(path, text)
        if errs:
            errors[path.name] = errs
        pages.append({"id": path.stem, "file": path.name, "meta": meta, "body": body})
    # related 必須互相列出：A 列了 B，B 也要列 A
    rel_map = {w["id"]: w["meta"].get("related", []) for w in weeks}
    for w in weeks:
        for r in rel_map[w["id"]] if isinstance(rel_map[w["id"]], list) else []:
            if r in rel_map and w["id"] not in rel_map[r]:
                errors.setdefault(w["file"], []).append(f"related 有 {r}，但 {r} 的 related 沒有列回 {w['id']}，請兩邊都加")
    weeks.sort(key=lambda w: int(w["meta"].get("week", 0)))
    return weeks, pages, errors


# ---------------------------------------------------------------- 輸出

def week_href(w, prefix):
    return f"{prefix}notes/{w['file'][:-3]}.html"


def sidebar(weeks, pages, prefix, current):
    items = []
    for w in weeks:
        cur = ' aria-current="page"' if current == w["id"] else ""
        items.append(
            f'<li><a href="{week_href(w, prefix)}"{cur}><span class="wk">W{int(w["meta"]["week"]):02d}</span>'
            f'<span>{html.escape(w["meta"]["title"])}</span></a></li>')
    extra = []
    for key, href, label in [("home", "index.html", "首頁"), ("keywords", "keywords.html", "關鍵字索引")] + \
            [(p["id"], f"{p['id']}.html", p["meta"]["title"]) for p in pages]:
        cur = ' aria-current="page"' if current == key else ""
        extra.append(f'<li><a href="{prefix}{href}"{cur}>{html.escape(label)}</a></li>')
    return (f'<ul class="nav-extra">{"".join(extra)}</ul>'
            f'<p class="nav-label">每週筆記</p><ul class="nav-weeks">{"".join(items)}</ul>')


def render(template, **kw):
    out = template
    for k, v in kw.items():
        out = out.replace("{{" + k + "}}", v)
    return out


def toc_html(toc):
    if not toc:
        return ""
    lis = "".join(f'<li class="l{lv}"><a href="#{a}">{inline(t)}</a></li>' for lv, t, a in toc)
    return f'<nav class="toc" aria-label="本頁目錄"><p class="toc-title">本頁目錄</p><ul>{lis}</ul></nav>'


def plain(md):
    t = re.sub(r"```.*?```", " ", md, flags=re.S)
    t = re.sub(r"[#>*`$\[\]]|\(http[^)]+\)|（p\.[^）]+）", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def build(weeks, pages):
    tpl = TEMPLATE.read_text(encoding="utf-8")
    OUT_NOTES.mkdir(exist_ok=True)
    for old in OUT_NOTES.glob("*.html"):
        old.unlink()
    by_id = {w["id"]: w for w in weeks}
    search = []

    for idx, w in enumerate(weeks):
        m = w["meta"]
        body_html, toc = markdown_to_html(w["body"])
        chips = "".join(f'<a class="chip" href="../keywords.html#{slugify(k)}">{html.escape(k)}</a>' for k in m["keywords"])
        rel = "".join(
            f'<a class="chip chip-rel" href="{week_href(by_id[r], "../")}">W{int(by_id[r]["meta"]["week"]):02d} {html.escape(by_id[r]["meta"]["title"])}</a>'
            for r in m["related"] if r in by_id)
        prev_w = weeks[idx - 1] if idx > 0 else None
        next_w = weeks[idx + 1] if idx + 1 < len(weeks) else None
        pn = '<nav class="prevnext">'
        pn += (f'<a class="prev" href="{week_href(prev_w, "../")}"><small>上一週</small>{html.escape(prev_w["meta"]["title"])}</a>'
               if prev_w else "<span></span>")
        pn += (f'<a class="next" href="{week_href(next_w, "../")}"><small>下一週</small>{html.escape(next_w["meta"]["title"])}</a>'
               if next_w else "<span></span>")
        pn += "</nav>"
        header = (f'<header class="note-head"><p class="eyebrow">第 {int(m["week"])} 週</p>'
                  f'<h1>{html.escape(m["title"])}</h1><p class="summary">{inline(m["summary"])}</p>'
                  f'<div class="chips">{chips}</div>'
                  f'<p class="source">資料來源：課堂投影片《{html.escape(m["slides"])}》，文中（p.12）代表投影片頁碼。</p></header>')
        footer_rel = f'<section class="related"><h2>相關筆記</h2><div class="chips">{rel}</div></section>' if rel else ""
        page = render(tpl, title=html.escape(f"W{int(m['week']):02d} {m['title']} · {SITE_TITLE}"),
                      description=html.escape(m["summary"]), prefix="../",
                      sidebar=sidebar(weeks, pages, "../", w["id"]), toc=toc_html(toc),
                      content=header + body_html + footer_rel + pn, site=SITE_TITLE)
        (OUT_NOTES / f"{w['file'][:-3]}.html").write_text(page, encoding="utf-8")
        search.append({"t": f"W{int(m['week']):02d} {m['title']}", "u": f"notes/{w['file'][:-3]}.html",
                       "s": m["summary"], "k": m["keywords"], "x": plain(w["body"])[:4000]})

    for p in pages:
        body_html, toc = markdown_to_html(p["body"])
        content = f'<header class="note-head"><h1>{html.escape(p["meta"]["title"])}</h1></header>' + body_html
        page = render(tpl, title=html.escape(f"{p['meta']['title']} · {SITE_TITLE}"),
                      description=html.escape(p["meta"].get("summary", SITE_TITLE)), prefix="",
                      sidebar=sidebar(weeks, pages, "", p["id"]), toc=toc_html(toc), content=content, site=SITE_TITLE)
        (ROOT / f"{p['id']}.html").write_text(page, encoding="utf-8")
        search.append({"t": p["meta"]["title"], "u": f"{p['id']}.html", "s": p["meta"].get("summary", ""),
                       "k": [], "x": plain(p["body"])[:2000]})

    # 首頁
    cards = "".join(
        f'<li><a class="card" href="{week_href(w, "")}"><span class="wk">W{int(w["meta"]["week"]):02d}</span>'
        f'<strong>{html.escape(w["meta"]["title"])}</strong><span class="card-sum">{inline(w["meta"]["summary"])}</span></a></li>'
        for w in weeks)
    intro_path = ROOT / "content" / "home.md"
    intro_html = markdown_to_html(intro_path.read_text(encoding="utf-8"))[0] if intro_path.exists() else ""
    home = (f'<header class="note-head"><p class="eyebrow">TAICA 生成式 AI 課程</p><h1>{SITE_TITLE}</h1></header>'
            f'{intro_html}<h2 id="weeks">每週筆記</h2><ul class="cards">{cards}</ul>')
    (ROOT / "index.html").write_text(render(tpl, title=SITE_TITLE, description="生成式 AI 課程的每週重點整理", prefix="",
                                            sidebar=sidebar(weeks, pages, "", "home"), toc="", content=home, site=SITE_TITLE),
                                     encoding="utf-8")

    # 關鍵字索引
    kw = {}
    for w in weeks:
        for k in w["meta"]["keywords"]:
            kw.setdefault(k, []).append(w)
    groups = []
    for k in sorted(kw, key=lambda s: s.lower()):
        links = "、".join(f'<a href="{week_href(w, "")}">W{int(w["meta"]["week"]):02d} {html.escape(w["meta"]["title"])}</a>'
                         for w in kw[k])
        groups.append(f'<li id="{slugify(k)}"><strong>{html.escape(k)}</strong><span>{links}</span></li>')
    kpage = (f'<header class="note-head"><h1>關鍵字索引</h1><p class="summary">每篇筆記的 keywords 會自動整理到這裡，'
             f'共 {len(kw)} 個。</p></header><ul class="kw-list">{"".join(groups)}</ul>')
    (ROOT / "keywords.html").write_text(render(tpl, title=f"關鍵字索引 · {SITE_TITLE}", description="關鍵字索引", prefix="",
                                                sidebar=sidebar(weeks, pages, "", "keywords"), toc="", content=kpage,
                                                site=SITE_TITLE), encoding="utf-8")
    (ROOT / "assets" / "search-index.js").write_text(
        "window.SEARCH_INDEX = " + json.dumps(search, ensure_ascii=False) + ";\n", encoding="utf-8")
    return len(weeks), len(pages), len(kw)


def main():
    weeks, pages, errors = load_all()
    if errors:
        print("格式檢查沒有通過：")
        for f, errs in errors.items():
            for e in errs:
                print(f"  ✗ {f}：{e}")
        sys.exit(1)
    print(f"✓ 格式檢查通過：{len(weeks)} 篇每週筆記、{len(pages)} 個其他頁面")
    if "--check" in sys.argv:
        return
    n_w, n_p, n_k = build(weeks, pages)
    print(f"✓ 已產生網站：index.html、keywords.html、{n_p} 個頁面、notes/ 底下 {n_w} 篇筆記、{n_k} 個關鍵字")


if __name__ == "__main__":
    main()
