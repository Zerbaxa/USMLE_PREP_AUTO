# MLE_PREP

UWorld 문제 하나 → 내 자료 전부 뒤져서 **출처 좌표가 달린 주제 노트** + **Anki 복습 카드**.

Claude Code 스킬(`/usmle`) + 로컬 검색 도구. 설치는 [SETUP.md](SETUP.md).

## 뭘 하는가

문제 해설(스크린샷 또는 UWorld Question Id)을 주면:

1. **내 자료를 뒤진다** — PDF·강의슬라이드는 텍스트로, UWorld 스크린샷은 OCR해서 sqlite FTS5 인덱스로
2. **Anki 컬렉션도 같이 뒤진다** — AnKing 덱의 `#UWorld::Step::<QID>` 태그로 그 문제 카드를 직접 찾는다
3. **노트를 쓴다** — 본문 각 줄에 `^[약칭]`, 하단에 **되찾을 수 있는 좌표**(파일명 + 페이지 / `nid:` / URL)
4. **검증한다** — `mle.py check`가 좌표 없는 인용을 잡아낸다
5. **Anki에 태그를 붙인다** — `ReviewNeeded` 태그 + suspend 해제 + AnkiWeb 동기화

핵심은 **좌표**다. 나중에 "이 문장 어디서 왔지?"를 항상 되짚을 수 있어야 노트가 쌓일 값어치가 있다.

## 명령

```bash
python3 mle.py index                   # 자료 인덱싱 (바뀐 것만, PNG는 OCR)
python3 mle.py qid 1841 [full]         # QID → UW 원문 + 그 문제 Anki 카드
python3 mle.py brief "주제"             # 로컬 전부 한 방에 (히트 + 원문 + Anki)
python3 mle.py search "주제"            # 히트 목록만
python3 mle.py page "파일명" 720-724     # 인덱스 원문 (PDF를 다시 열지 않는다)
python3 mle.py tag Nitrates            # Anki 태그 훑기
python3 mle.py mark [wide]             # ReviewNeeded 태그 + suspend 해제 + 동기화
python3 mle.py deck                    # Anki 쿼리·현황
python3 mle.py check "노트.md"          # 인용 좌표 누락 검사
python3 mle.py selftest
./progress.sh                          # OCR 진행률
```

## 구성

| 파일 | 무엇 |
| --- | --- |
| `mle.py` | 인덱싱·검색·Anki 연동 (약 380줄, 의존성 `pdftotext` 하나) |
| `ocr.swift` | macOS Vision OCR. 새 의존성 0 |
| `SKILL.md` | Claude Code 스킬 정의 — `~/.claude/skills/usmle/` 로 복사 |
| `paths.json` | 자기 경로 설정 (**커밋되지 않음**, `paths.example.json` 참고) |
| `materials.db` | 인덱스 (**커밋되지 않음** — 아래) |

## materials.db는 레포에 없다

인덱스에는 First Aid·Boards&Beyond·UWorld·Pathoma **원문이 그대로** 들어간다.
공유하면 자료 재배포가 되므로 커밋하지 않는다.

**각자 자기 자료로 `mle.py index`를 돌리면 같은 인덱스가 만들어진다.** 그게 원래 설계다.
PDF는 금방이고, 스크린샷 OCR만 장당 0.25초쯤 걸린다.

## Anki 연동

- 고정 쿼리 **`tag:ReviewNeeded`** — 노트가 늘어도 안 바뀐다
- Filtered Deck은 한 번만 만들면 된다 (`F` → `tag:ReviewNeeded`, **`is:due` 지우기**, Limit 500, Reschedule 체크)
- 이후엔 `mle.py mark` 실행 후 덱에서 **Rebuild**만
- **Anki 컬렉션에 직접 쓰지 않는다.** 태그 추가와 suspend 해제만 AnkiConnect 경유
- Anki가 켜져 있으면 WAL 잠금 때문에 못 읽으므로 스냅샷을 떠서 읽는다

AnKing 덱은 카드가 전부 suspended라 태그만 붙이면 filtered deck에 **0장**이 잡힌다.
`mark`가 suspend까지 풀어주는 이유다.

## 알려진 함정

- **QID가 같아도 같은 문제가 아닐 수 있다.** Step1·Step2·COMLEX가 번호를 따로 매기고 연도판마다 재번호된다.
  `qid`가 본문을 같이 찍으니 반드시 눈으로 대조할 것
- **PDF 페이지 ≠ 책 인쇄 페이지** (First Aid는 22쪽 차이). 인용은 양쪽 다 표기
- **Sketchy는 그림 위주**라 텍스트가 드문드문만 잡힌다. Anki `#Sketchy*` 태그로 보완
- PDF 줄바꿈에서 하이픈이 사라진다 (`hormone-sensitive` → `hormonesensitive`).
  OR 질의라 대개 다른 단어로 걸리지만, 구절 검색은 실패할 수 있다
- OCR `.fast` 모드는 5배 빠르지만 `Question Id` 같은 작은 글씨를 놓쳐 못 쓴다
- Vision은 Neural Engine을 직렬로 써서 **병렬화가 안 먹는다** (~0.25초/장이 하드웨어 바닥)

## 라이선스

도구 부분은 자유롭게. 학습 자료는 각자 알아서.
