#!/usr/bin/env python3
"""USMLE 자료 검색 — 내 PDF 인덱스 + Anki 콜렉션.

  ./mle.py index                        자료 폴더 인덱싱 (바뀐 파일만)
  ./mle.py mark [wide|주제]             ★ 오답 카드에 ReviewNeeded 태그 (AnkiConnect)
  ./mle.py deck                         태그 수동으로 붙일 때 쓸 nid 목록
  ./mle.py brief "aortic stenosis"      ★ 로컬 전부 한 방에 (히트+원문+Anki)
  ./mle.py search "aortic stenosis"     히트 목록만
  ./mle.py page Biochemistry 720-724    인덱스에 있는 원문 그대로
  ./mle.py fig FA2026 347 [x,y,w,h 이름]  ★ 원본 그림을 오려 vault Assets/Images에
  ./mle.py tag firstaid                 Anki 태그 훑기
"""
import html
import pathlib
import json
import re
import shutil
import sqlite3
import subprocess
import sys

HERE = pathlib.Path(__file__).parent


def _conf():
    """경로 설정. `paths.json`이 있으면 그걸 쓰고, 없으면 기본값.
    개인 경로가 레포에 들어가지 않게 paths.json은 gitignore 대상이다."""
    f = HERE / "paths.json"
    c = json.loads(f.read_text()) if f.exists() else {}
    home = pathlib.Path.home()
    roots = [pathlib.Path(p).expanduser() for p in c.get("materials", [])] or [home / "USMLE_Materials"]
    topics = pathlib.Path(c.get("topics", home / "USMLE_Notes/Topics")).expanduser()
    anki = c.get("anki")
    if anki:
        anki = pathlib.Path(anki).expanduser()
    else:  # Anki 프로필명은 사람마다 다르다. 가장 큰 컬렉션을 고른다.
        cands = sorted((home / "Library/Application Support/Anki2").glob("*/collection.anki2"),
                       key=lambda p: p.stat().st_size, reverse=True)
        anki = cands[0] if cands else home / "Library/Application Support/Anki2/User 1/collection.anki2"
    return roots, topics, anki, c.get("tag", "ReviewNeeded")


ROOTS, TOPICS, ANKI, TAG = _conf()
INDEX = HERE / "materials.db"
SNAP = HERE / "anki_snapshot.anki2"  # Anki 켜져 있을 때 읽을 사본
LIMIT = 12


def db():
    c = sqlite3.connect(INDEX)
    c.execute("create table if not exists files(path primary key, stamp)")
    c.execute("create virtual table if not exists pages using fts5(text, path unindexed, page unindexed)")
    return c


OCR_BIN = HERE / "ocr"
EXTS = (".pdf", ".md", ".txt", ".png")


def pages_of(p):
    """(page_no, text) 목록. PDF는 pdftotext, 나머지는 통째로 1페이지."""
    if p.suffix.lower() == ".pdf":
        out = subprocess.run(["pdftotext", "-q", str(p), "-"], capture_output=True, text=True).stdout
        return [(i, t) for i, t in enumerate(out.split("\f"), 1) if t.strip()]
    return [(1, p.read_text(errors="replace"))]


def ocr_batch(paths, c, chunk=300):
    """스크린샷은 macOS Vision으로 OCR. 프로세스를 매번 띄우지 않게 묶어서 넘긴다.
    ponytail: Vision이 Neural Engine을 직렬로 써서 병렬화가 안 먹는다(~0.25초/장).
    .fast 모드는 5배 빠르지만 'Question Id' 같은 작은 글씨를 통째로 놓쳐 못 쓴다."""
    if not OCR_BIN.exists():
        return print(f"  ! OCR 미빌드 — swiftc -O ocr.swift -o ocr 실행 필요 (PNG {len(paths)}장 건너뜀)")
    done = 0
    for i in range(0, len(paths), chunk):
        batch = paths[i:i + chunk]
        out = subprocess.run([str(OCR_BIN)], input="\n".join(str(p) for p in batch),
                             capture_output=True, text=True).stdout
        for blob in out.split("\x01")[1:]:
            path, _, text = blob.partition("\n")
            if not text.strip():
                continue
            c.execute("delete from pages where path=?", (path,))
            c.execute("insert into pages(text,path,page) values(?,?,1)", (text, path))
        for p in batch:
            st = p.stat()
            c.execute("insert or replace into files values(?,?)",
                      (str(p), f"{st.st_mtime_ns}:{st.st_size}"))
        c.commit()
        done += len(batch)
        print(f"  OCR {done}/{len(paths)}장", flush=True)


def index():
    c, n, seen, shots = db(), 0, set(), []
    known = dict(c.execute("select path, stamp from files"))
    for root in ROOTS:
        root.mkdir(parents=True, exist_ok=True)
        for p in sorted(root.rglob("*")):
            if p.suffix.lower() not in EXTS or p.name.startswith("."):
                continue
            key, stamp = str(p), f"{p.stat().st_mtime_ns}:{p.stat().st_size}"
            seen.add(key)
            if known.get(key) == stamp:
                continue
            if p.suffix.lower() == ".png":
                shots.append(p)
                continue
            c.execute("delete from pages where path=?", (key,))
            pages = pages_of(p)
            c.executemany("insert into pages(text,path,page) values(?,?,?)",
                          [(t, key, pg) for pg, t in pages])
            c.execute("insert or replace into files values(?,?)", (key, stamp))
            c.commit()  # 중간에 끊겨도 여기까지는 남는다
            n += 1
            print(f"  + {p.relative_to(root)} ({len(pages)}p)" + ("  ← 텍스트 없음(이미지 PDF)" if not pages else ""))
    if shots:
        print(f"스크린샷 {len(shots)}장 OCR 시작 (~{len(shots) * 0.25 / 60:.0f}분)")
        ocr_batch(shots, c)
    for gone in set(known) - seen:
        c.execute("delete from pages where path=?", (gone,))
        c.execute("delete from files where path=?", (gone,))
    c.commit()
    total = c.execute("select count(*) from pages").fetchone()[0]
    print(f"{n + len(shots)}개 파일 갱신, 총 {total}페이지 인덱스.")


def terms(q):
    # ponytail: PDF 줄바꿈에서 하이픈이 없어져 'hormone-sensitive'가 'hormonesensitive'로 들어간다.
    # OR 질의라 다른 단어로 대개 걸리므로 방치. 검색이 실제로 헛치기 시작하면 붙인 형태도 같이 질의할 것.
    return [w for w in re.findall(r"[\w'-]+", q) if len(w) > 2]


def search_materials(q):
    if not INDEX.exists():
        print("[내 자료] 인덱스 없음 — ./mle.py index 먼저 실행")
        return []
    expr = " OR ".join(f'"{w}"' for w in terms(q)) or f'"{q}"'
    rows = db().execute(
        "select path, page, snippet(pages,0,'**','**','…',20) from pages "
        "where pages match ? order by bm25(pages) limit ?", (expr, LIMIT)).fetchall()
    print(f"\n## 내 자료 ({len(rows)})")
    for path, page, snip in rows:
        print(f"- `{pathlib.Path(path).name}` p.{page} — {' '.join(snip.split())}")
    return rows


def page(pat, rng):
    """인덱스에 있는 원문을 그대로 꺼낸다. pdftotext 다시 돌리지 말 것."""
    a, _, b = rng.partition("-")
    for p, pg, t in db().execute(
            "select path, page, text from pages where path like ? and page between ? and ? "
            "order by path, page", (f"%{pat}%", int(a), int(b or a))):
        print(f"\n----- {pathlib.Path(p).name} p.{pg}\n{t.strip()}")


def brief(q, ctx=3):
    """로컬 소스 한 방에: 히트 목록 + 상위 히트 페이지 원문 + Anki. 툴 왕복 1회."""
    rows = search_materials(q)
    print(f"\n## 상위 히트 원문 ({min(ctx, len(rows))}개)")
    for path, pg, _ in rows[:ctx]:
        t = db().execute("select text from pages where path=? and page=?", (path, pg)).fetchone()
        print(f"\n----- {pathlib.Path(path).name} p.{pg}\n{t[0].strip()[:1500]}")
    ws = terms(q) or [q]
    anki(" and ".join(["flds like ?"] * len(ws)), [f"%{w}%" for w in ws], "본문")


def anki_db():
    """Anki가 켜져 있으면 WAL 잠금 때문에 원본을 읽기전용으로 못 연다.
    그때는 스냅샷을 떠서 읽는다. 원본에는 절대 쓰지 않는다."""
    try:
        c = sqlite3.connect(f"file:{ANKI}?mode=ro", uri=True)
        c.execute("select 1 from notes limit 1").fetchone()
        return c
    except sqlite3.Error:
        pass
    if not SNAP.exists() or SNAP.stat().st_mtime_ns < ANKI.stat().st_mtime_ns:
        for suf in ("", "-wal", "-shm"):
            src = pathlib.Path(str(ANKI) + suf)
            if src.exists():
                shutil.copy2(src, str(SNAP) + suf)
        print("  (Anki 실행 중 → 스냅샷으로 읽음)")
    return sqlite3.connect(SNAP)  # 내 복사본이라 쓰기 열기 안전, WAL 복구 가능


def anki(where, args, label):
    try:
        rows = anki_db().execute(f"select id, flds, tags from notes where {where} limit ?",
                                 (*args, LIMIT)).fetchall()
    except sqlite3.Error as e:
        return print(f"\n## Anki — 읽기 실패({e}). Anki를 닫고 다시 실행.")
    print(f"\n## Anki {label} ({len(rows)})")
    for nid, flds, tags in rows:
        text = html.unescape(re.sub(r"<[^>]+>", " ", flds.replace("\x1f", " ⟶ ")))
        src = [t for t in tags.split() if "::#" in t or t.startswith("#AK_Step")]
        print(f"- `nid:{nid}` {' '.join(text.split())[:300]}")
        if src:
            print(f"    출처태그: {' '.join(src[:4])}")


AC = "http://127.0.0.1:8765"


def anki_connect(action, **params):
    """AnkiConnect. 쓰기는 addTags와 unsuspend만 쓴다.
    AnKing 덱은 전 카드가 suspended라 태그만 붙이면 filtered deck에 0장 잡힌다.
    카드 내용·스케줄·덱 이동은 건드리지 않는다."""
    import json
    import urllib.request
    body = json.dumps({"action": action, "version": 6, "params": params}).encode()
    with urllib.request.urlopen(AC, body, timeout=15) as r:
        res = json.load(r)
    if res.get("error"):
        raise RuntimeError(res["error"])
    return res["result"]


def collect(topic=""):
    """오답 노트들에서 (인용 nid, 주제 태그) 를 긁는다."""
    # rglob: 주제 노트가 과목 폴더 안에 있다. 루트의 MOC도 걸리지만 nid/AK 태그가 없어 무해.
    files = sorted(TOPICS.rglob(f"*{topic}*.md")) if topic else sorted(TOPICS.rglob("*.md"))
    nids, tags = set(), set()
    for f in files:
        t = f.read_text()
        nids |= set(re.findall(r"nid:(\d+)", t))
        tags |= set(re.findall(r"`(#AK_Step\d_v\d+::[^`\s]+)`", t))
    return files, sorted(nids), sorted(tags)


def mark(arg=""):
    """인용 카드에 ReviewNeeded 태그를 붙인다. `mark wide` 면 주제 전체로 넓힌다."""
    wide = arg.strip() == "wide"
    files, nids, tags = collect("" if wide else arg)
    if not files:
        return print("노트 없음")
    try:
        anki_connect("version")
    except Exception as e:
        return print(f"AnkiConnect 연결 안 됨 ({e})\n  → Anki를 껐다 켜면 붙는다. 그전엔 `mle.py deck`으로 수동.")
    if wide:
        target = set()
        for t in tags:
            target |= set(anki_connect("findNotes", query=f'"tag:{t}*"'))
    else:
        target = {int(n) for n in nids}
    already = set(anki_connect("findNotes", query=f"tag:{TAG}"))
    todo = sorted(target - already)
    if todo:
        anki_connect("addTags", notes=todo, tags=TAG)
    # AnKing은 전 카드가 suspended → 풀어주지 않으면 filtered deck이 0장을 잡는다
    frozen = anki_connect("findCards", query=f"tag:{TAG} is:suspended")
    if frozen:
        anki_connect("unsuspend", cards=frozen)
    live = len(anki_connect("findCards", query=f"tag:{TAG} -is:suspended"))
    print(f"노트 {len(files)}개 · 대상 {len(target)}장 → 새로 붙임 {len(todo)}장 "
          f"(이미 붙어있던 것 {len(target & already)}장)")
    print(f"suspend 해제 {len(frozen)}장 · 지금 바로 볼 수 있는 카드 {live}장")
    # 로컬에만 있으면 폰에서 안 보인다. 바로 올린다.
    try:
        anki_connect("sync")
        print("AnkiWeb 동기화 완료 — 아이폰에서 당기면 보인다")
    except Exception as e:
        print(f"동기화 실패 ({e}) — Anki에서 `Y` 직접 누를 것")
    print(f"Anki에서 `tag:{TAG}` — 덱에서 Rebuild 누르면 들어온다")


def deck(topic=""):
    """오답 노트에 실제로 인용한 카드만 뽑아 Anki 검색 쿼리를 만든다.
    Anki > Tools > Create Filtered Deck에 붙여넣기. 덱 파일은 건드리지 않는다."""
    files, nids, tags = collect(topic)
    if not files:
        return print(f"노트 없음: {TOPICS}")
    wide = " or ".join(f'"tag:{t}*"' for t in tags)
    try:
        cur = anki_db()
        have = {str(r[0]) for r in cur.execute(
            f"select id from notes where tags like ? and id in ({','.join(nids)})", (f"%{TAG}%",))}
        broad = {str(r[0]) for t in tags for r in cur.execute(
            "select id from notes where tags like ?", (f"%{t}%",))}
        broad_new = sorted(broad - {str(r[0]) for r in cur.execute(
            "select id from notes where tags like ?", (f"%{TAG}%",))})
    except sqlite3.Error as e:
        return print(f"Anki 읽기 실패: {e}")
    todo = [n for n in nids if n not in have]

    print(f"노트 {len(files)}개 · 인용 카드 {len(nids)}장 · 주제 전체 {len(broad)}장\n")
    print(f"■ 공부할 때 쓰는 고정 쿼리 (이건 영원히 안 바뀐다)\n    tag:{TAG}\n")
    if todo:
        print(f"■ 이번에 태그 붙일 카드 {len(todo)}장 — 인용한 것만 (좁게)")
        print(f"    nid:{','.join(todo)}\n")
        print(f"■ 주제 전체로 넓히려면 {len(broad_new)}장")
        print(f"    {wide}\n")
        print(f"  Anki에서 `B` → 위 줄 붙여넣기 → ⌘A 전체선택 → ⌘⇧A → `{TAG}` 입력")
    else:
        print(f"■ 새로 붙일 카드 없음 — 인용 카드 {len(nids)}장 모두 `{TAG}` 태그가 붙어 있다")
    print(f"\n  Filtered Deck은 한 번만 만들면 된다 (`F` → Search에 `tag:{TAG}`)")
    print("  ⚠ 기본으로 들어있는 `is:due`를 지울 것 — 안 그러면 new 카드가 하나도 안 잡힌다")
    print("  ⚠ Limit을 넉넉히(500), 'Reschedule cards based on my answers' 체크")
    print("  이후엔 태그만 붙이고 덱에서 Rebuild 누르면 새 카드가 따라 들어온다")


def qid(n, full=False):
    """UWorld Question Id로 직행. AnKing 카드에 ::<QID> 태그가 박혀 있고, 내 UW 자료에도 원문이 있다.
    `qid <번호> full` 이면 해설 전문을 다 찍는다 — 번호만 받고 노트를 쓸 때 쓴다.
    ⚠ QID는 Step1/Step2/COMLEX가 따로 매기고 연도판마다 재번호된다. 같은 번호 = 같은 문제가 아니다.
    그래서 본문을 함께 찍는다 — 반드시 눈으로 대조하고 쓸 것."""
    if not n.isdigit():
        return print("QID는 숫자여야 한다")
    rows = db().execute(
        "select path, page, text from pages where pages match ? and path like '%UWORLD%'",
        (f'"Question Id: {n}"',)).fetchall()
    print(f"\n## 내 UWorld 자료 ({len(rows)})  ※ 아래 본문이 지금 문제와 같은 내용인지 확인할 것")
    for p, pg, t in rows:
        s = " ".join(t.split())
        # UI 잡음(툴바·주소창) 뒤부터 보여줘야 실제 문제 텍스트가 나온다
        i = max(s.find("Question Id"), 0)
        print(f"- `{pathlib.Path(p).name}` p.{pg}\n    {s[i:i + (99999 if full else 260)]}")
    anki("tags like ?", [f"%::{n} %"], f"QID {n} 카드 (내용 대조 필수)")


def _vault():
    """Obsidian vault 루트 = topics에서 위로 올라가며 `.obsidian`이 있는 곳."""
    for p in [TOPICS, *TOPICS.parents]:
        if (p / ".obsidian").is_dir():
            return p
    return TOPICS


def fig(args):
    """해설의 그림을 그대로 오려 vault에 넣는다. 새로 그리는 것보다 정확하다.

      fig "FA2026" 347                      페이지 전체를 임시 png로 뽑는다 → Read로 열어보고 좌표를 정한다
      fig "FA2026" 347 120,300,900,600 FA-p347_Murmurs    그 영역만 잘라 Assets/Images/에 저장
      fig ~/Desktop/shot.png 0,80,1200,700 UW_1234_AS     스크린샷도 같은 방식(페이지 번호 없음)

    좌표는 렌더된 png 기준 x,y,w,h. 이름을 안 주면 임시 파일 경로만 찍고 끝난다.
    ⚠ 이름이 곧 vault 전체에서의 이름이다 — 출처가 보이게 (`UW_<QID>_…` / `FA-p<쪽>_…`)."""
    page_no = crop = name = ""
    src, *rest = args
    for a in rest:
        if a.isdigit():
            page_no = a
        elif "," in a:
            crop = a
        else:
            name = a
    p = pathlib.Path(src).expanduser()
    if p.is_file() and p.suffix.lower() != ".pdf":
        img = p
    else:
        if not p.is_file():  # 파일명 일부만 줘도 인덱스에서 찾는다
            hit = db().execute("select path from pages where path like ? limit 1",
                               (f"%{src}%",)).fetchone()
            if not hit:
                return print(f"'{src}' — 인덱스에 없는 파일")
            p = pathlib.Path(hit[0])
        if not page_no:
            return print("PDF는 페이지 번호가 필요하다")
        img = HERE / ".fig" / f"{p.stem}_p{page_no}.png"
        img.parent.mkdir(exist_ok=True)
        subprocess.run(["pdftoppm", "-r", "150", "-f", page_no, "-l", page_no, "-png",
                        "-singlefile", str(p), str(img.with_suffix(""))], check=True)
    if crop:
        x, y, w, h = (int(v) for v in crop.split(","))
        out = HERE / ".fig" / f"{img.stem}_crop.png"  # 원본 옆에 두면 vault가 지저분해진다
        out.parent.mkdir(exist_ok=True)
        subprocess.run(["sips", "-c", str(h), str(w), "--cropOffset", str(y), str(x),
                        str(img), "--out", str(out)], capture_output=True, check=True)
        img = out
    size = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(img)],
                          capture_output=True, text=True).stdout.split()
    wh = f"{size[-3]}x{size[-1]}" if len(size) >= 4 else "?"
    if not name:
        return print(f"{img}  ({wh})\n  ← Read로 열어보고 crop 좌표(x,y,w,h)와 이름을 정해 다시 호출")
    dest = _vault() / "Assets/Images" / f"{name}.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(img, dest)
    print(f"{dest}  ({wh})\n노트에 붙일 줄:  ![[{name}.png]]")


def check(path):
    """노트의 ^[약칭]이 전부 ## 출처에 정의돼 있는지. 좌표 없는 인용 = 되찾을 수 없는 인용."""
    body, _, src = pathlib.Path(path).read_text().partition("## 출처")
    if not src:
        return print("✗ `## 출처` 섹션이 없다")
    # ^[A] 뿐 아니라 ^[A][B][C]처럼 이어붙인 것도 전부 잡는다
    used = {r for run in re.findall(r"\^((?:\[[^\]]+\])+)", body)
            for r in re.findall(r"\[([^\]]+)\]", run)}
    defined = set(re.findall(r"`\[([^\]]+)\]`", src))
    dangling, unused = sorted(used - defined), sorted(defined - used)
    # nid는 실제로 Anki에 있어야 한다. 자리표시자(`nid:1471554...`)를 적어놓는 사고를 잡는다.
    nids = set(re.findall(r"nid:(\d+)", body + src))
    ghosts = []
    if nids:
        try:
            live = {str(r[0]) for r in anki_db().execute(
                f"select id from notes where id in ({','.join(nids)})")}
            ghosts = sorted(nids - live)
        except sqlite3.Error:
            pass  # Anki를 못 읽으면 이 검사만 건너뛴다
    print(f"{pathlib.Path(path).name}: 인용 {len(used)}종 / 출처 {len(defined)}종 / nid {len(nids)}개")
    for d in dangling:
        print(f"  ✗ `^[{d}]` — 출처에 정의 없음")
    for g in ghosts:
        print(f"  ✗ `nid:{g}` — Anki에 없는 카드")
    for u in unused:
        print(f"  · `[{u}]` — 출처에만 있고 본문에서 안 씀")
    if not dangling and not ghosts:
        print("  ✓ 모든 인용에 좌표 있음")
    return not dangling and not ghosts


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    q = " ".join(sys.argv[2:])
    if cmd == "index":
        index()
    elif cmd == "search" and q:
        search_materials(q)
        ws = terms(q) or [q]
        anki(" and ".join(["flds like ?"] * len(ws)), [f"%{w}%" for w in ws], "본문")
    elif cmd == "brief" and q:
        brief(q)
    elif cmd == "deck":
        deck(q)
    elif cmd == "mark":
        mark(q)
    elif cmd == "qid" and q:
        parts = q.split()
        qid(parts[0], full=len(parts) > 1 and parts[1] == "full")
    elif cmd == "check" and q:
        check(q)
    elif cmd == "page" and len(sys.argv) > 3:
        page(sys.argv[2], sys.argv[3])
    elif cmd == "fig" and q:
        fig(sys.argv[2:])
    elif cmd == "tag" and q:
        anki("tags like ?", [f"%{q}%"], f"태그 '{q}'")
    elif cmd == "selftest":
        selftest()
    else:
        print(__doc__)


def selftest():
    global ROOTS, INDEX
    import tempfile
    d = pathlib.Path(tempfile.mkdtemp())
    MATERIALS, INDEX = d / "mat", d / "i.db"
    ROOTS = [MATERIALS]
    MATERIALS.mkdir()
    (MATERIALS / "fa.md").write_text("Aortic stenosis: late-peaking systolic murmur.")
    index()
    assert db().execute("select count(*) from pages").fetchone()[0] == 1
    index()  # 두 번째는 mtime 같으니 재파싱 없음
    assert db().execute("select count(*) from pages").fetchone()[0] == 1, "중복 삽입"
    (MATERIALS / "fa.md").unlink()
    index()
    assert db().execute("select count(*) from pages").fetchone()[0] == 0, "삭제 반영 안 됨"
    print("selftest ok")


if __name__ == "__main__":
    main()
