#!/usr/bin/env bash
# ============================================================
# ติดตั้งและตรวจสอบระบบ Inventory Management System แบบอัตโนมัติ
# (Linux / macOS / Git Bash บน Windows)
#
# ใช้ทดสอบ Clean Environment Installation: สร้าง virtual environment (.venv),
# ติดตั้ง dependency, สร้างฐานข้อมูล inventory.db จาก schema.sql, (เลือกได้) ใส่ seed data
# แล้วตรวจว่าระบบใช้งานได้จริงด้วย smoke test, self-test, pytest, Flake8 และ Bandit
#
# วิธีใช้:  bash scripts/setup.sh [--clean] [--seed] [--skip-tests]
#   --clean       ลบ .venv และ inventory.db เดิมก่อนติดตั้ง (ข้อมูลในฐานข้อมูลจะหายถาวร)
#   --seed        ใส่ข้อมูลสินค้าตัวอย่างจาก seed_data.sql
#   --skip-tests  ข้ามการติดตั้งเครื่องมือทดสอบและการรัน pytest / Flake8 / Bandit
#
# รันจากโฟลเดอร์ไหนก็ได้ สคริปต์จะย้ายไปทำงานที่ root ของโปรเจกต์ให้เอง
# คืนค่า exit code 0 เมื่อทุกขั้นผ่าน และ 1 เมื่อมีขั้นใดล้มเหลว
# ============================================================
set -u

CLEAN=0
SEED=0
SKIP_TESTS=0
for arg in "$@"; do
    case "$arg" in
        --clean) CLEAN=1 ;;
        --seed) SEED=1 ;;
        --skip-tests) SKIP_TESTS=1 ;;
        -h|--help) sed -n '2,17p' "$0"; exit 0 ;;
        *) echo "ไม่รู้จักตัวเลือก: $arg (ดู --help)"; exit 2 ;;
    esac
done

export PYTHONIOENCODING=utf-8
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT" || exit 1

if [ -t 1 ]; then
    C_CYAN=$'\033[36m'; C_GREEN=$'\033[32m'; C_RED=$'\033[31m'; C_YELLOW=$'\033[33m'; C_OFF=$'\033[0m'
else
    C_CYAN=""; C_GREEN=""; C_RED=""; C_YELLOW=""; C_OFF=""
fi

STEP_NO=0
RESULTS=()
FAILED=0

step() {
    STEP_NO=$((STEP_NO + 1))
    printf '\n%s[%d] %s%s\n' "$C_CYAN" "$STEP_NO" "$1" "$C_OFF"
}

result() {  # result <ชื่อขั้น> <0=ผ่าน|อื่นๆ=ล้มเหลว> [รายละเอียด]
    local name="$1" rc="$2" detail="${3:-}"
    if [ "$rc" -eq 0 ]; then
        RESULTS+=("PASS  $name  $detail")
        printf '    %sPASS%s %s\n' "$C_GREEN" "$C_OFF" "$detail"
    else
        RESULTS+=("FAIL  $name  $detail")
        FAILED=$((FAILED + 1))
        printf '    %sFAIL%s %s\n' "$C_RED" "$C_OFF" "$detail"
    fi
}

summary() {
    printf '\n%s==================== สรุปผลการติดตั้ง ====================%s\n' "$C_CYAN" "$C_OFF"
    for line in "${RESULTS[@]}"; do
        echo "  $line"
    done
    if [ "$FAILED" -eq 0 ]; then
        printf '%sติดตั้งและตรวจสอบสำเร็จทุกขั้น เริ่มใช้งานด้วย: %s inventory_app.py%s\n' "$C_GREEN" "${VENV_PY:-python}" "$C_OFF"
    else
        printf '%sมี %d ขั้นที่ล้มเหลว ดูรายละเอียดด้านบน%s\n' "$C_RED" "$FAILED" "$C_OFF"
    fi
}

abort() {
    printf '    %s%s%s\n' "$C_RED" "$1" "$C_OFF"
    summary
    exit 1
}

echo "${C_CYAN}Inventory Management System - Automated Setup (Linux / macOS / Git Bash)${C_OFF}"
echo "โฟลเดอร์โปรเจกต์: $REPO_ROOT"
echo "ตัวเลือก: clean=$CLEAN seed=$SEED skip-tests=$SKIP_TESTS"

# ------------------------------------------------------------
step "ตรวจสอบ Python 3.10 ขึ้นไป"
PY=""
for cand in python3 python; do
    if command -v "$cand" >/dev/null 2>&1 && \
       "$cand" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >/dev/null 2>&1; then
        PY="$cand"
        break
    fi
done
if [ -z "$PY" ]; then
    result "Python >= 3.10" 1 "ไม่พบ Python 3.10 ขึ้นไป"
    abort "ติดตั้ง Python 3.10+ (เช่น sudo apt install python3 python3-venv) แล้วรันสคริปต์นี้ใหม่"
fi
result "Python >= 3.10" 0 "($PY -> Python $("$PY" -c 'import platform; print(platform.python_version())'))"

# ------------------------------------------------------------
if [ "$CLEAN" -eq 1 ]; then
    step "ล้างสภาพแวดล้อมเดิม (--clean)"
    echo "    ${C_YELLOW}คำเตือน: กำลังลบ .venv และ inventory.db (ข้อมูลในฐานข้อมูลจะหายถาวร)${C_OFF}"
    rm -rf .venv inventory.db
    if [ ! -e .venv ] && [ ! -e inventory.db ]; then
        result "Clean environment" 0 "ลบ .venv และ inventory.db แล้ว"
    else
        result "Clean environment" 1 "ลบไฟล์เดิมไม่สำเร็จ"
        abort "อาจมีโปรแกรมเปิดไฟล์อยู่"
    fi
fi

# ------------------------------------------------------------
step "สร้าง virtual environment (.venv)"
venv_python() {  # Linux/macOS ใช้ bin/ ส่วน Git Bash บน Windows ใช้ Scripts/
    if [ -x .venv/bin/python ]; then echo "$REPO_ROOT/.venv/bin/python"
    elif [ -x .venv/Scripts/python.exe ]; then echo "$REPO_ROOT/.venv/Scripts/python.exe"
    fi
}
VENV_PY="$(venv_python)"
if [ -n "$VENV_PY" ]; then
    result "Virtual environment" 0 "มี .venv อยู่แล้ว ใช้ของเดิม"
else
    if ! "$PY" -m venv .venv; then
        result "Virtual environment" 1 "python -m venv ล้มเหลว"
        abort "บน Debian/Ubuntu ให้ติดตั้งแพ็กเกจ venv ก่อน: sudo apt install python3-venv"
    fi
    VENV_PY="$(venv_python)"
    [ -n "$VENV_PY" ] || abort "สร้าง .venv แล้วแต่ไม่พบ python ภายใน"
    result "Virtual environment" 0 "สร้าง .venv ใหม่"
fi

# ------------------------------------------------------------
# pip ที่มากับ venv อาจมีช่องโหว่ CVE-2026-13346 (PYSEC-2026-3721) ที่แก้แล้วใน pip 26.2
# ดู documents/Dependency_Security_Audit_Report.md
step "อัปเกรด pip ใน .venv เป็นเวอร์ชันที่ไม่มีช่องโหว่ที่ทราบ (>= 26.2)"
"$VENV_PY" -m pip install --disable-pip-version-check -q --upgrade "pip>=26.2"
rc=$?
result "Upgrade pip" "$rc" "pip $("$VENV_PY" -c 'import pip; print(pip.__version__)')"

# ------------------------------------------------------------
if [ "$SKIP_TESTS" -eq 1 ]; then
    step "ติดตั้ง dependency"
    result "Install dependencies" 0 "ข้าม (--skip-tests) ตัวโปรแกรมใช้แค่ standard library"
else
    step "ติดตั้ง dependency จาก requirements-dev.txt"
    if "$VENV_PY" -m pip install --disable-pip-version-check -q -r requirements-dev.txt; then
        result "Install dependencies" 0 "pytest, pytest-cov, flake8, bandit"
    else
        result "Install dependencies" 1 "pip install ล้มเหลว"
        abort "ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต แล้วรันใหม่"
    fi
fi

# ------------------------------------------------------------
step "สร้างฐานข้อมูล inventory.db จาก schema.sql"
"$VENV_PY" - <<'PYEOF'
import sqlite3
con = sqlite3.connect("inventory.db")
con.executescript(open("schema.sql", encoding="utf-8").read())
con.commit()
con.close()
PYEOF
rc=$?
result "Create database" "$rc" "schema.sql"
[ "$rc" -eq 0 ] || abort "สร้างฐานข้อมูลไม่สำเร็จ"

# ------------------------------------------------------------
if [ "$SEED" -eq 1 ]; then
    step "ใส่ข้อมูลตัวอย่างจาก seed_data.sql"
    "$VENV_PY" - <<'PYEOF'
import sqlite3
con = sqlite3.connect("inventory.db")
con.executescript(open("seed_data.sql", encoding="utf-8").read())
con.commit()
con.close()
PYEOF
    rc=$?
    result "Seed data" "$rc" "seed_data.sql"
    [ "$rc" -eq 0 ] || abort "ใส่ seed data ไม่สำเร็จ"
fi

# ------------------------------------------------------------
step "ตรวจสอบโครงสร้างฐานข้อมูล"
MIN_PRODUCTS=0
[ "$SEED" -eq 1 ] && MIN_PRODUCTS=3
MIN_PRODUCTS="$MIN_PRODUCTS" "$VENV_PY" - <<'PYEOF'
import os
import sqlite3
import sys
con = sqlite3.connect("inventory.db")
names = {r[0] for r in con.execute("SELECT name FROM sqlite_master")}
need = {"products", "stock_movements", "action_logs", "idx_products_barcode_unique", "trg_products_updated_at"}
missing = sorted(need - names)
count = con.execute("SELECT COUNT(*) FROM products").fetchone()[0] if "products" in names else -1
print(f"    ตาราง/ดัชนี/trigger ที่ขาด: {missing or 'ไม่มี'} | จำนวนสินค้า: {count}")
sys.exit(0 if not missing and count >= int(os.environ["MIN_PRODUCTS"]) else 1)
PYEOF
result "Verify database" "$?" "ต้องมีตารางครบ และสินค้าอย่างน้อย $MIN_PRODUCTS รายการ"

# ------------------------------------------------------------
step "Smoke test: เปิดโปรแกรมแล้วเลือกเมนู 8 (ออก)"
out="$(printf '8\n' | "$VENV_PY" inventory_app.py)"
rc=$?
if [ "$rc" -eq 0 ] && printf '%s' "$out" | grep -q "ขอบคุณที่ใช้บริการ"; then
    result "Smoke test" 0 "exit code $rc"
else
    result "Smoke test" 1 "exit code $rc"
fi

# ------------------------------------------------------------
step "Self-test: python inventory_app.py --selftest"
out="$("$VENV_PY" inventory_app.py --selftest)"
rc=$?
if [ "$rc" -eq 0 ] && printf '%s' "$out" | grep -q "ครบถ้วน 100%"; then
    result "Self-test" 0 "exit code $rc"
else
    result "Self-test" 1 "exit code $rc"
fi

# ------------------------------------------------------------
if [ "$SKIP_TESTS" -eq 0 ]; then
    step "PyTest + Coverage (เกณฑ์ >= 90%)"
    "$VENV_PY" -m pytest -q --cov
    result "PyTest + Coverage" "$?"

    step "Flake8"
    "$VENV_PY" -m flake8 --count .
    result "Flake8" "$?"

    step "Bandit"
    "$VENV_PY" -m bandit -q -c pyproject.toml -r .
    result "Bandit" "$?"
fi

summary
[ "$FAILED" -eq 0 ]
