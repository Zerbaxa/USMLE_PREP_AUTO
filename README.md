# MLE_PREP — USMLE 오답 → 출처 달린 리뷰 노트 → Anki

UWorld 문제 하나 → 내 자료 전부 뒤져서 **좌표 달린 주제 노트** + **Anki 복습 카드**.

## 상태 (2026-07-27 기준)

| | |
| --- | --- |
| 인덱스 | **47,939페이지** — PDF·문서 25,919 + UWorld 스크린샷 OCR 22,020 |
| UWorld QID 커버 | **3,738개** (스크린샷 20,486장, QID당 평균 5.5컷) |
| 주제 노트 | 9개 (`Topics/`) |
| Anki `ReviewNeeded` | 노트 15 → 카드 19장 |
| 시험 | **2027년 1월** |

## 다시 시작할 때

이 폴더를 열고 아래를 실행하면 이어집니다. 세션이 바뀌어도 상태는 전부 파일에 있습니다.

```bash
cd ~/Claude/MLE_PREP
python3 mle.py index      # 자료 새로 넣었으면
python3 mle.py deck       # 지금 Anki 상태 확인
```

작업 방식은 `~/.claude/skills/usmle/SKILL.md` 에 있습니다. Claude Code에서 **`/usmle`** 로 부르거나
스크린샷을 드래그하면 자동으로 걸립니다.

## 쓰는 법

**① 번호만 주기 (권장)** — "QID 1841, C 골랐고 맞음"
→ DB에서 해설을 꺼내고 지문을 보여드림 → 같은 문제 확인 → 노트 생성
→ DB에 없거나 내용이 다르면 알려드림. **도표가 있는 문제는 캡처가 낫습니다** (OCR로 그림 구조는 안 잡힘)

**② 스크린샷 드래그** — 화면 전체. 항상 동작함

## 명령

```bash
python3 mle.py qid 1841 [full]   # QID → UW 원문 + 그 문제 Anki 카드 (full이면 해설 전문)
python3 mle.py brief "주제"       # 로컬 전부 한 방에 (히트+원문+Anki), 0.2초
python3 mle.py search "주제"      # 히트 목록만
python3 mle.py page "파일명" 720-724   # 인덱스 원문. pdftotext 다시 돌리지 말 것
python3 mle.py tag Nitrates      # Anki 태그 훑기
python3 mle.py mark [wide]       # ReviewNeeded 태그 + suspend 해제 + AnkiWeb 동기화
python3 mle.py deck              # Anki 쿼리·현황
python3 mle.py check "노트.md"    # 인용 좌표 누락 검사
python3 mle.py index             # 자료 인덱싱 (바뀐 것만, PNG는 OCR)
python3 mle.py selftest
./progress.sh                    # OCR 진행률
```

## 어디에 뭐가 있나

| 무엇 | 어디 |
| --- | --- |
| 작업 방식 | `~/.claude/skills/usmle/SKILL.md` |
| 검색 도구 | `mle.py` (이 폴더) |
| OCR | `ocr.swift` → `ocr` (macOS Vision, 의존성 0) |
| 인덱스 | `materials.db` (sqlite FTS5) |
| 자료 원본 | OneDrive `30_Study_Resources/Medical/USMLE` + `~/Documents/USMLE_Materials` |
| Anki | `~/Library/Application Support/Anki2/Minkyo/collection.anki2` |
| 주제 노트 | `Sync_Vault/40_Study/CBBSA Study/Topics/*.md` |
| 복습 큐 | `Sync_Vault/40_Study/CBBSA Study/USMLE_Review.md` |

## Anki

- 고정 쿼리 **`tag:ReviewNeeded`** — 노트가 늘어도 안 바뀜
- Filtered Deck은 한 번만 만들면 됨 (`F` → `tag:ReviewNeeded`, **`is:due` 지우기**, Limit 500, Reschedule 체크)
- `mle.py mark`가 태그·suspend 해제·동기화까지 함. 사용자는 **Rebuild**만
- AnkiWeb 계정 **`excist@korea.ac.kr`** (아이폰도 같은 계정이어야 함)
- 덱 설정: 복습 상한 9999, **최대 간격 150일**(시험 D-172 기준), FSRS 켜짐
  → 한 달쯤 돌린 뒤 Deck Options에서 **Optimize** 누를 것

## 알아둘 것

- 의존성 0개. `pdftotext`(homebrew) + python stdlib(sqlite3 FTS5) + macOS Vision(Swift)
- Anki가 켜져 있으면 스냅샷을 떠서 읽음. **원본에는 절대 쓰지 않음** (태그·suspend는 AnkiConnect 경유)
- **QID가 같아도 같은 문제가 아닐 수 있다** — Step1/Step2/COMLEX 별도 번호, 연도판마다 재번호. 본문 대조 필수
- 스크린샷은 **2023 UWorld**. 2026판에서 개정됐을 수 있음
- Sketchy는 그림 위주라 텍스트가 드문드문만 잡힘 (OCR 미적용). Anki `#Sketchy*` 태그로 보완
- mp4 강의(24GB)는 인덱싱 안 함
- PDF 페이지 ≠ 책 인쇄 페이지 (FA는 22쪽 차이). 인용은 양쪽 다 표기
