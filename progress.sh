#!/bin/sh
# OCR 진행률. 로그 생성시각 기준 실측 속도와 ETA.
L=/tmp/ocr_run.log
D=$(grep -o 'OCR [0-9]*/' "$L" 2>/dev/null | tail -1 | tr -dc 0-9)
T=$(grep -o '스크린샷 [0-9]*장' "$L" 2>/dev/null | tr -dc 0-9)
python3 - "${D:-0}" "${T:-1}" "$(stat -f %B "$L" 2>/dev/null || echo 0)" <<'PY'
import sys, time
d, t, birth = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
e = int(time.time()) - birth if birth else 0
w = 40; f = int(d / t * w)
print(f"[{'█'*f}{'░'*(w-f)}] {d/t*100:5.1f}%  {d:,}/{t:,}장")
if e and d:
    r = d / e
    print(f"경과 {e//60}분 · {r:.1f}장/초 · 남은 시간 약 {int((t-d)/r//60)}분")
else:
    print("측정 중…")
PY
