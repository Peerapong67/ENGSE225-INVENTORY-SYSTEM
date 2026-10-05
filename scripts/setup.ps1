<#
.SYNOPSIS
    ติดตั้งและตรวจสอบระบบ Inventory Management System แบบอัตโนมัติ (Windows)

.DESCRIPTION
    ใช้ทดสอบ Clean Environment Installation: สร้าง virtual environment (.venv),
    ติดตั้ง dependency, สร้างฐานข้อมูล inventory.db จาก schema.sql, (เลือกได้) ใส่ seed data
    แล้วตรวจว่าระบบใช้งานได้จริงด้วย smoke test, self-test, pytest, Flake8 และ Bandit

    รันจากโฟลเดอร์ไหนก็ได้ สคริปต์จะย้ายไปทำงานที่ root ของโปรเจกต์ให้เอง
    คืนค่า exit code 0 เมื่อทุกขั้นผ่าน และ 1 เมื่อมีขั้นใดล้มเหลว

.PARAMETER Clean
    ลบ .venv และ inventory.db เดิมก่อนติดตั้ง (ข้อมูลในฐานข้อมูลจะหายถาวร)
    ใช้เมื่อต้องการจำลองเครื่องที่เพิ่งติดตั้งใหม่

.PARAMETER Seed
    ใส่ข้อมูลสินค้าตัวอย่างจาก seed_data.sql หลังสร้างฐานข้อมูล

.PARAMETER SkipTests
    ข้ามการติดตั้งเครื่องมือทดสอบและการรัน pytest / Flake8 / Bandit
    (ยังรัน smoke test และ self-test ตามปกติ)

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 -Clean -Seed
#>
param(
    [switch]$Clean,
    [switch]$Seed,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$script:Results = New-Object System.Collections.ArrayList
$script:StepNo = 0

function Write-Step([string]$Title) {
    $script:StepNo++
    Write-Host ""
    Write-Host "[$script:StepNo] $Title" -ForegroundColor Cyan
}

function Add-Result([string]$Name, [bool]$Passed, [string]$Detail = "") {
    [void]$script:Results.Add([pscustomobject]@{ Step = $Name; Result = $(if ($Passed) { "PASS" } else { "FAIL" }); Detail = $Detail })
    if ($Passed) {
        Write-Host "    PASS $Detail" -ForegroundColor Green
    } else {
        Write-Host "    FAIL $Detail" -ForegroundColor Red
    }
}

function Show-Summary {
    Write-Host ""
    Write-Host "==================== สรุปผลการติดตั้ง ====================" -ForegroundColor Cyan
    $script:Results | Format-Table -AutoSize | Out-String | Write-Host
    $failed = @($script:Results | Where-Object { $_.Result -eq "FAIL" }).Count
    if ($failed -eq 0) {
        Write-Host "ติดตั้งและตรวจสอบสำเร็จทุกขั้น เริ่มใช้งานด้วย: .venv\Scripts\python.exe inventory_app.py" -ForegroundColor Green
    } else {
        Write-Host "มี $failed ขั้นที่ล้มเหลว ดูรายละเอียดด้านบน" -ForegroundColor Red
    }
    return $failed
}

function Stop-Setup([string]$Message) {
    Write-Host "    $Message" -ForegroundColor Red
    [void](Show-Summary)
    exit 1
}

# รันโค้ด Python โดยเขียนลงไฟล์ชั่วคราว (UTF-8) แล้วรันไฟล์นั้น
# ไม่ pipe โค้ดหรือ input เข้า python ตรงๆ เพราะ PowerShell 5.1 แปลงข้อความที่ pipe เข้า
# native process เป็น ASCII ($OutputEncoding) ตัวอักษรไทยจึงกลายเป็น "?" และ input
# อาจไปไม่ถึงโปรแกรม (พบตอนทดสอบ Clean Environment Installation)
function Invoke-PythonCode([string]$Python, [string]$Code) {
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("inventory_setup_" + [guid]::NewGuid().ToString("N") + ".py")
    [System.IO.File]::WriteAllText($tmp, $Code, (New-Object System.Text.UTF8Encoding $false))
    try {
        # Out-Host: ส่ง output ไปหน้าจอ ไม่ให้ปนกับค่า exit code ที่ return
        & $Python $tmp | Out-Host
        return $LASTEXITCODE
    } finally {
        Remove-Item $tmp -ErrorAction SilentlyContinue
    }
}

Write-Host "Inventory Management System - Automated Setup (Windows)" -ForegroundColor Cyan
Write-Host "โฟลเดอร์โปรเจกต์: $RepoRoot"
Write-Host "ตัวเลือก: Clean=$Clean Seed=$Seed SkipTests=$SkipTests"

# ------------------------------------------------------------
Write-Step "ตรวจสอบ Python 3.10 ขึ้นไป"
$PyCmd = $null
$candidates = @(@("py", "-3"), @("python"), @("python3"))
foreach ($c in $candidates) {
    $exe = $c[0]
    $pre = @($c | Select-Object -Skip 1)
    if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) { continue }
    try {
        & $exe @pre -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) { $PyCmd = $c; break }
    } catch { continue }
}
if ($null -eq $PyCmd) {
    Add-Result "Python >= 3.10" $false "ไม่พบ Python 3.10 ขึ้นไป"
    Stop-Setup "ติดตั้ง Python จาก https://www.python.org/downloads/ แล้วรันสคริปต์นี้ใหม่"
}
$PyExe = $PyCmd[0]
$PyPre = @($PyCmd | Select-Object -Skip 1)
$version = & $PyExe @PyPre -c "import platform; print(platform.python_version())"
Add-Result "Python >= 3.10" $true "($($PyCmd -join ' ') -> Python $version)"

# ------------------------------------------------------------
if ($Clean) {
    Write-Step "ล้างสภาพแวดล้อมเดิม (-Clean)"
    Write-Host "    คำเตือน: กำลังลบ .venv และ inventory.db (ข้อมูลในฐานข้อมูลจะหายถาวร)" -ForegroundColor Yellow
    foreach ($target in @(".venv", "inventory.db")) {
        if (Test-Path $target) { Remove-Item $target -Recurse -Force }
    }
    $gone = -not (Test-Path ".venv") -and -not (Test-Path "inventory.db")
    Add-Result "Clean environment" $gone "ลบ .venv และ inventory.db แล้ว"
    if (-not $gone) { Stop-Setup "ลบไฟล์เดิมไม่สำเร็จ (อาจมีโปรแกรมเปิดไฟล์อยู่)" }
}

# ------------------------------------------------------------
Write-Step "สร้าง virtual environment (.venv)"
$VenvPy = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (Test-Path $VenvPy) {
    Add-Result "Virtual environment" $true "มี .venv อยู่แล้ว ใช้ของเดิม"
} else {
    & $PyExe @PyPre -m venv .venv
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $VenvPy)) {
        Add-Result "Virtual environment" $false "python -m venv ล้มเหลว"
        Stop-Setup "สร้าง .venv ไม่สำเร็จ"
    }
    Add-Result "Virtual environment" $true "สร้าง .venv ใหม่"
}

# ------------------------------------------------------------
# pip ที่มากับ venv อาจมีช่องโหว่ CVE-2026-13346 (PYSEC-2026-3721) ที่แก้แล้วใน pip 26.2
# ดู documents/Dependency_Security_Audit_Report.md
Write-Step "อัปเกรด pip ใน .venv เป็นเวอร์ชันที่ไม่มีช่องโหว่ที่ทราบ (>= 26.2)"
& $VenvPy -m pip install --disable-pip-version-check -q --upgrade "pip>=26.2"
$pipVersion = & $VenvPy -c "import pip; print(pip.__version__)"
Add-Result "Upgrade pip" ($LASTEXITCODE -eq 0) "pip $pipVersion"

# ------------------------------------------------------------
if ($SkipTests) {
    Write-Step "ติดตั้ง dependency"
    Add-Result "Install dependencies" $true "ข้าม (-SkipTests) ตัวโปรแกรมใช้แค่ standard library"
} else {
    Write-Step "ติดตั้ง dependency จาก requirements-dev.txt"
    & $VenvPy -m pip install --disable-pip-version-check -q -r requirements-dev.txt
    if ($LASTEXITCODE -ne 0) {
        Add-Result "Install dependencies" $false "pip install ล้มเหลว"
        Stop-Setup "ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต แล้วรันใหม่"
    }
    Add-Result "Install dependencies" $true "pytest, pytest-cov, flake8, bandit"
}

# ------------------------------------------------------------
Write-Step "สร้างฐานข้อมูล inventory.db จาก schema.sql"
$rc = Invoke-PythonCode $VenvPy @"
import sqlite3
con = sqlite3.connect("inventory.db")
con.executescript(open("schema.sql", encoding="utf-8").read())
con.commit()
con.close()
"@
Add-Result "Create database" ($rc -eq 0) "schema.sql"
if ($rc -ne 0) { Stop-Setup "สร้างฐานข้อมูลไม่สำเร็จ" }

# ------------------------------------------------------------
if ($Seed) {
    Write-Step "ใส่ข้อมูลตัวอย่างจาก seed_data.sql"
    $rc = Invoke-PythonCode $VenvPy @"
import sqlite3
con = sqlite3.connect("inventory.db")
con.executescript(open("seed_data.sql", encoding="utf-8").read())
con.commit()
con.close()
"@
    Add-Result "Seed data" ($rc -eq 0) "seed_data.sql"
    if ($rc -ne 0) { Stop-Setup "ใส่ seed data ไม่สำเร็จ" }
}

# ------------------------------------------------------------
Write-Step "ตรวจสอบโครงสร้างฐานข้อมูล"
$minProducts = $(if ($Seed) { 3 } else { 0 })
$rc = Invoke-PythonCode $VenvPy @"
import sqlite3, sys
con = sqlite3.connect("inventory.db")
names = {r[0] for r in con.execute("SELECT name FROM sqlite_master")}
need = {"products", "stock_movements", "action_logs", "idx_products_barcode_unique", "trg_products_updated_at"}
missing = sorted(need - names)
count = con.execute("SELECT COUNT(*) FROM products").fetchone()[0] if "products" in names else -1
print(f"    ตาราง/ดัชนี/trigger ที่ขาด: {missing or 'ไม่มี'} | จำนวนสินค้า: {count}")
sys.exit(0 if not missing and count >= $minProducts else 1)
"@
Add-Result "Verify database" ($rc -eq 0) "ต้องมีตารางครบ และสินค้าอย่างน้อย $minProducts รายการ"

# ------------------------------------------------------------
Write-Step "Smoke test: เปิดโปรแกรมแล้วเลือกเมนู 8 (ออก)"
$rc = Invoke-PythonCode $VenvPy @"
import subprocess, sys
proc = subprocess.run([sys.executable, "inventory_app.py"], input="8\n", capture_output=True,
                      text=True, encoding="utf-8")
print(f"    exit code ของโปรแกรม: {proc.returncode}")
if proc.stderr.strip():
    print(proc.stderr)
sys.exit(0 if proc.returncode == 0 and "ขอบคุณที่ใช้บริการ" in proc.stdout else 1)
"@
Add-Result "Smoke test" ($rc -eq 0) "เมนูหลักแสดงผลและออกจากโปรแกรมได้"

# ------------------------------------------------------------
Write-Step "Self-test: python inventory_app.py --selftest"
$out = & $VenvPy inventory_app.py --selftest | Out-String
$ok = ($LASTEXITCODE -eq 0) -and ($out -match "ครบถ้วน 100%")
Add-Result "Self-test" $ok "exit code $LASTEXITCODE"

# ------------------------------------------------------------
if (-not $SkipTests) {
    Write-Step "PyTest + Coverage (เกณฑ์ >= 90%)"
    & $VenvPy -m pytest -q --cov
    Add-Result "PyTest + Coverage" ($LASTEXITCODE -eq 0) "exit code $LASTEXITCODE"

    Write-Step "Flake8"
    & $VenvPy -m flake8 --count .
    Add-Result "Flake8" ($LASTEXITCODE -eq 0) "exit code $LASTEXITCODE"

    Write-Step "Bandit"
    & $VenvPy -m bandit -q -c pyproject.toml -r .
    Add-Result "Bandit" ($LASTEXITCODE -eq 0) "exit code $LASTEXITCODE"
}

$failed = Show-Summary
if ($failed -eq 0) { exit 0 } else { exit 1 }
