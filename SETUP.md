# 설치 (다른 컴퓨터에서 처음 쓸 때)

macOS 기준. 의존성은 `pdftotext` 하나뿐이고 나머지는 시스템에 이미 있는 것을 쓴다.

## 1. 준비물

```bash
brew install poppler          # pdftotext
xcode-select --install        # Swift (OCR용). 이미 있으면 건너뜀
```

- **Anki** + **AnkiConnect** 애드온
  Tools → Add-ons → Get Add-ons → `2055492159` → Anki 재시작
- **Obsidian vault** — 아무 폴더나. 안에 `Topics/` 하위폴더만 있으면 된다

## 2. 경로 4개 수정

`mle.py` 맨 위 상수를 자기 환경에 맞춘다.

| 줄 | 상수 | 무엇으로 |
| --- | --- | --- |
| 20 | `ROOTS` | 자기 자료 폴더 (PDF·스크린샷이 있는 곳). 여러 개 가능 |
| 25 | `ANKI` | Anki 프로필 경로. `Anki2/<프로필명>/collection.anki2` |
| 182 | `TOPICS` | 자기 vault의 `Topics/` 경로 |
| 183 | `TAG` | 그대로 `ReviewNeeded` 둬도 됨 |

`~/.claude/skills/usmle/SKILL.md` 안에도 vault 경로와 `mle.py` 경로가 박혀 있으니 같이 바꾼다.

## 3. 빌드 & 인덱싱

```bash
swiftc -O ocr.swift -o ocr     # 한 번만
python3 mle.py selftest        # 동작 확인
python3 mle.py index           # 자료 읽기
```

PDF는 빠르다. **스크린샷은 OCR이라 장당 약 0.25초** — 2만 장이면 2시간쯤 걸린다.
백그라운드로 돌리고 `./progress.sh`로 진행률을 본다. 중간에 끊겨도 이어서 한다.

## 4. Anki 준비

```bash
python3 mle.py mark            # 태그 + suspend 해제 + 동기화
```

Anki에서 `F` → Create Filtered Deck
- Search: `tag:ReviewNeeded`
- **기본으로 들어있는 `is:due`를 지울 것** — AnKing 카드는 전부 new라 안 지우면 0장 잡힌다
- Limit: 500 / Reschedule 체크

한 번만 만들면 되고, 이후엔 `mark` 실행 후 덱에서 **Rebuild**만 누른다.

## 5. 스킬 설치

`SKILL.md`를 `~/.claude/skills/usmle/SKILL.md` 로 복사한다.
Claude Code에서 `/usmle` 로 부르거나 UWorld 스크린샷을 드래그하면 걸린다.

---

## 안 들어있는 것

**`materials.db`는 레포에 없다.** 상용 교재 원문이 그대로 들어있는 파일이라 공유하지 않는다.
각자 자기 자료로 `index`를 돌리면 같은 인덱스가 만들어진다 — 그게 원래 설계다.

`Topics/*.md` 노트도 이 레포에 없다. 각자 vault에 쌓인다.
서로 주고받고 싶으면 노트 파일만 따로 보내면 된다 — 출처가 `파일명 + 페이지`라 상대 자료에서도 같은 곳을 찾아갈 수 있다.

## Windows / Linux

`ocr.swift`는 macOS Vision 전용이라 안 된다. PDF·텍스트 검색은 그대로 동작하고,
스크린샷 OCR만 빠진다. 필요하면 `pages_of()`의 `.png` 분기를 tesseract로 갈아끼우면 된다.
