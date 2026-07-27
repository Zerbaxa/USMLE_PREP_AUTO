---
name: usmle
description: UWorld 문제 해설(스크린샷/텍스트)을 받아 내 자료·Anki·온라인을 전부 검색해서 출처 표기된 주제별 리뷰 노트를 Obsidian에 만든다. "이거 정리해줘", "UWorld 오답", "이 문제 틀렸어", "위키에 넣어줘", "이 주제 정리해줘", 문제 해설 스크린샷을 드래그했을 때 사용.
---

# USMLE 주제 리뷰 노트 (`/usmle`)

UWorld 해설 한 장 → **그 주제에 대한 내 모든 자료를 한 노트로 모은다.**
해설 내용 + 내 PDF 자료 + Anki 카드 + 온라인 근거, **전부 출처를 달아서** 원문을 되찾을 수 있게.

- vault: `/Users/minkyo/Documents/Sync_Vault/40_Study/CBBSA Study`
- 주제 노트: `Topics/<주제명>.md` ← 결과물
- 과목 노트: `*.md` ← 여기엔 `[[링크]]` 한 줄만 추가
- 복습 큐: `USMLE_Review.md`
- 검색 도구: `python3 /Users/minkyo/Claude/MLE_PREP/mle.py`

## 절차

### 1. 해설 읽기
스크린샷에서 **이미지에 있는 것만** 뽑는다.
- 주제(진단명/개념) — 노트 파일명이 된다
- 정답의 핵심 근거 / 헷갈린 오답의 감별점 (오답이 진짜 학습포인트)
- 표·수치는 마크다운 표로 그대로

흐리거나 잘려서 확신이 안 서면 **추측하지 말고 묻는다.**

### 2. 이미 있는지 확인
```
ls "…/CBBSA Study/Topics/"
```
같은 주제 노트가 있으면 **새로 만들지 말고 그 노트를 보강**한다 (기존 줄은 안 고침, 새 내용만 추가).

### 3. 세 군데 검색 — 셋 다 한다

**스크린샷에 `Question Id`가 보이면 그것부터.** 키워드 검색보다 훨씬 정확하다:
```bash
M="python3 /Users/minkyo/Claude/MLE_PREP/mle.py"
$M qid 161      # 그 문제의 UW PDF 원문 페이지 + 그 문제용으로 만들어진 Anki 카드 직행
```
AnKing 카드에는 `#UWorld::Step::<QID>` 태그가 박혀 있다(Step1 12,086 / Step2 10,957장).
QID가 안 보이면 사용자에게 물어봐도 좋다 — 한 번 물어보는 값이 키워드 검색 여러 번보다 싸다.

**⚠ 같은 QID = 같은 문제가 아니다.** Step1·Step2·COMLEX가 번호를 따로 매기고, 연도판마다 재번호된다.
`qid`가 찍어주는 본문을 **반드시 눈으로 대조**하고, 내용이 다르면 그 히트는 버린다.
노트에 쓸 때도 "QID 일치"가 아니라 **내용이 일치함을 확인했다**는 근거로 쓴다.

**그 다음 로컬은 한 번에 끝낸다. `brief` 하나면 된다** (0.2초):
```bash
$M brief "aortic stenosis murmur"     # 히트 목록 + 상위 히트 원문 + Anki 본문, 전부 한 방에
```
필요할 때만 추가로:
```bash
$M page "Cardiology Slides" 405-412   # 인덱스 원문 그대로. 다른 페이지가 더 필요할 때만
$M tag "Aortic_Stenosis"              # Anki 태그로 훑기
```

- **PDF를 `pdftotext`/Read로 다시 열지 마라.** 17,000여 페이지가 이미 인덱스에 텍스트로 들어있다.
  원문이 더 필요하면 `page` 명령을 쓴다. 파일 경로를 찾을 필요도 없다(파일명 일부만 주면 됨).
- **온라인 검색은 기본적으로 하지 않는다.** 내 자료 + Anki + 네가 아는 USMLE high-yield 수준이면 충분하다.
  PubMed·원저 논문은 찾지 마라 — Step 시험 범위를 넘고 노트만 무거워진다.
  내 자료가 통째로 비어서 확인이 필요할 때만 StatPearls/AAFP 정도를 한 번 본다.
- **내 지식으로 채운 줄은 `^[HY]`로 표시**하고 `## 출처`에 `- \`[HY]\` USMLE high-yield 일반지식 (자료 출처 없음)`을 둔다.
  좌표 있는 줄과 섞이지 않게 하는 게 요점이다.
- **Anki**: `출처태그`에 `#FirstAid::07_Cardiovascular::…` 같은 원본 챕터가 박혀 있다 — 그게 곧 출처다.
- **온라인**: WebSearch로 보충. **1차 자료 우선** (StatPearls, NIH/NCBI, UpToDate 공개분, 학회 가이드라인, AAFP). 블로그·요약사이트는 쓰지 않는다. 근거로 쓸 페이지는 WebFetch로 실제로 열어보고 인용한다.

검색어는 해설의 핵심 용어로. 한 번에 안 걸리면 동의어·약어로 2~3번 더 (예: `HCM` / `hypertrophic cardiomyopathy`).
**아무것도 안 나온 소스는 "없었다"고 노트에 적는다.** 조용히 빼지 않는다.

### 4. 노트 작성 — `Topics/<주제>.md`
한국어 설명 + 의학용어는 영어. 기존 노트 스타일(`###` + 중첩 불릿, 비교는 표) 유지.

```markdown
# Aortic stenosis

> 출처: UWorld 오답 2026-07-27 · 자료 3 · Anki 5 · 온라인 2

## 핵심
- Crescendo-decrescendo systolic murmur, carotid로 방사
	- 심해질수록 peak가 늦어짐(late-peaking) → severe 시사 ^[UW]
- **vs HCM**: Valsalva에서 AS는 murmur 감소, HCM은 증가 (preload↓ → outflow obstruction↑) ^[UW][FA]

## 감별
| | Valsalva | Handgrip | 방사 |
| --- | --- | --- | --- |
| AS | ↓ | ↓ | carotid |
| HCM | ↑ | ↓ | 없음 |

## 내 자료에서
- Severe AS 기준: valve area <1.0 cm², mean gradient >40 mmHg ^[FA-p.301]

## Anki
- `nid:1471558760048` murmur 모양 = crescendo-decrescendo, soft S2 동반
- 관련 태그: `#AK_Step1_v12::#FirstAid::07_Cardiovascular::…::Aortic_Stenosis`

## 온라인
- 무증상 severe AS도 EF<50%면 AVR 적응 ^[SP]

## 출처
- `[UW]` UWorld 해설 (2026-07-27 오답)
- `[FA-p.301]` First_Aid_2025.pdf p.301 — `~/Documents/USMLE_Materials/`
- `[AK]` Anki `nid:1471558760048` · AnKing Step Deck
- `[SP]` StatPearls, Aortic Stenosis — https://www.ncbi.nlm.nih.gov/books/NBK…

## 관련
[[Hypertrophic cardiomyopathy]] · [[Cardiology]]

## Anki로 돌리기
`nid:1471558760048,1471554803766` — 이 카드들에 `오답` 태그 붙이기
`"tag:#AK_Step1_v12::#FirstAid::07_Cardiovascular::03_Physiology::10_Heart_Murmurs*"` — 주제 전체
```

`## Anki로 돌리기` 섹션은 항상 넣는다.

### 태그는 내가 붙인다 — 노트 저장 직후 실행
```bash
$M mark            # 인용한 카드에 ReviewNeeded 태그 (AnkiConnect)
$M mark wide       # 주제 전체로 넓힐 때
```
- 공부용 쿼리는 언제나 **`tag:ReviewNeeded`** 하나로 고정. 노트가 늘어도 안 바뀐다.
- **태그 외에는 절대 건드리지 않는다.** 카드 내용·스케줄·덱 이동 금지. `addTags`만 쓴다.
- AnkiConnect가 안 붙으면(Anki 꺼짐) `$M deck`으로 nid 줄을 주고 수동 안내한다.
- 붙인 뒤 보고에 "N장 태그됨, 덱에서 Rebuild" 한 줄 넣는다.

출처 표기 규칙: 본문 각 줄 끝에 `^[약칭]`, 아래 `## 출처`에서 약칭 → **되찾을 수 있는 좌표**(파일명+페이지 / `nid:` / URL)로 푼다. 좌표 없는 출처는 쓰지 않는다.

**PDF 페이지 ≠ 책 인쇄 페이지.** First Aid는 22쪽 차이(PDF p.347 = 책 p.325). 인쇄 번호는
페이지 원문 안에 찍혀 있으니 그대로 읽어서 `FA2026.pdf p.347 (책 p.325)`처럼 둘 다 적는다.

### 5. 연결
- 과목 노트(`Cardiology.md` 등) 끝에 `- [[Aortic stenosis]]` 한 줄. 과목이 애매하면 묻는다.
- 관련 주제 노트가 이미 있으면 서로 `[[링크]]`.

### 6. 복습 큐
`USMLE_Review.md` 표에 한 줄 (없으면 헤더까지 만든다).

| 날짜 | 과목 | 주제 | 왜 틀렸나 |
| --- | --- | --- | --- |
| 2026-07-27 | Cardiology | [[Aortic stenosis]] | HCM과 Valsalva 반응 반대인 걸 헷갈림 |

"왜 틀렸나"는 지식 부족인지 함정인지 구분해 **한 줄로 구체적으로**.

**맞힌 문제(정리 목적)면 복습 큐에 넣지 않는다.** 오답 신호가 흐려진다. 노트 헤더에만
`(정답 맞힘, 정리용)`으로 남긴다. 오답인지 아닌지 안 밝혔으면 물어본다.

### 7. 인용 검사 — 빼먹지 말 것
```bash
$M check "…/Topics/<주제>.md"
```
`✗ 출처에 정의 없음`이 뜨면 고친 뒤에 보고한다. 좌표 없는 인용은 이 프로젝트의 존재 이유를 깬다.

### 8. 보고
어느 노트를 만들었고 각 소스에서 몇 건 나왔는지 2~3줄. 여러 장이면 한꺼번에 처리하고 마지막에 한 번만.

## 규칙

- **좌표 없는 내용은 안 쓴다.** 내 기억으로 보충하고 싶으면 `[확인 필요]` 표시하고 출처 없음을 명시.
- 문제 지문·선택지를 통째로 옮기지 않는다. 학습포인트만 (저작권 + 나중에 노이즈).
- 환자 식별정보 금지.
- 기존 노트의 문장은 고치지 않는다. 틀린 게 보이면 말만 하고 승인받는다.
- 이미지 파일을 vault로 복사하지 않는다. 텍스트로 정리한다.
- **해설의 도표·흐름도는 반드시 옮긴다.** 표는 마크다운 표로, **흐름도는 mermaid 코드블록**으로
  (Obsidian이 네이티브로 렌더링한다). 그림이 그 문제의 뼈대인 경우가 많다 — 빼먹으면 노트가 반쪽이 된다.
- **노트에 쓸 때 `printf`/`echo`를 쓰지 마라.** 본문에 `%`가 있으면 줄이 잘린다(실제로 겪음).
  Write/Edit 툴로 쓴다. 기존 파일에 덧붙일 때는 파일 끝 개행 여부를 먼저 확인한다.

## 자료 폴더

인덱싱 대상 (둘 다):
- `~/Library/CloudStorage/OneDrive-개인/30_Study_Resources/Medical/USMLE` — Pathoma, Boards&Beyond(BNB2024/BNBS2)
- `~/Documents/USMLE_Materials` — 그때그때 던져넣는 곳

```bash
python3 /Users/minkyo/Claude/MLE_PREP/mle.py index   # 바뀐 파일만 다시 읽음
```
새 자료를 넣었는데 검색에 안 잡히면 이걸 먼저 돌린다.

**Sketchy는 그림 위주라 텍스트가 드문드문만 잡힌다** (OCR 미적용). Sketchy 내용은 Anki의
`#Sketchy*` 태그로 보완한다: `mle.py tag SketchyPharm`
