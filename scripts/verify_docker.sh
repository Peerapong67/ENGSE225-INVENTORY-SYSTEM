#!/bin/sh
# ตรวจ Docker image หลัง build: docker build -t engse225-inventory-system:2.0.1 .
# รัน: sh scripts/verify_docker.sh  (ต้องมี Docker; ขั้นตอน pip-audit ต้องต่ออินเทอร์เน็ต)
IMG=engse225-inventory-system:2.0.1
VOL=inventory-verify-$$
PASS=0; FAIL=0
check() { if [ "$1" = 0 ]; then echo "PASS  $2"; PASS=$((PASS+1)); else echo "FAIL  $2"; FAIL=$((FAIL+1)); fi; }

echo "DOCKER IMAGE VERIFICATION - $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "docker: $(docker --version)"
docker image inspect $IMG --format 'image id={{.Id}}
size={{.Size}} bytes | user={{.Config.User}} | workdir={{.Config.WorkingDir}} | cmd={{.Config.Cmd}} | volumes={{.Config.Volumes}}'
echo

echo "== 1) menus 1-8 (stdin script, docker run -i, volume $VOL)"
OUT=$(printf '2\nD1\nDocker Item\n3\n10\nA\n\n\n1\n\n3\nD1\n1\n4\n5\nDocker\n\n6\n7\n\n9\n8\n' | docker run -i --rm -v $VOL:/data $IMG 2>&1)
RC=$?
echo "$OUT" | grep -E "บันทึกสำเร็จ|ตัดสต็อกสำเร็จ|คำเตือน|Export สำเร็จ|ตัวเลือกไม่ถูกต้อง|ขอบคุณ|Traceback" | sed 's/^.*: \(บันทึก\|ตัด\|Export\)/\1/'
MISSING=""
for m in "บันทึกสำเร็จ" "รายการสินค้าทั้งหมดในระบบ" "ตัดสต็อกสำเร็จ" "จำนวนชนิดสินค้าทั้งหมด: 1" "ผลการค้นหา 'Docker'" "รวม 1 รายการที่ต้องสั่งซื้อเพิ่ม" "Export สำเร็จ: 1 รายการ" "ขอบคุณที่ใช้บริการ"; do
  echo "$OUT" | grep -qF "$m" || MISSING="$MISSING [$m]"
done
echo "exit=$RC missing_markers=${MISSING:-none}"
echo "$OUT" | grep -q Traceback; TB=$?
[ $RC = 0 ] && [ -z "$MISSING" ] && [ $TB = 1 ]; check $? "menus 1-8 in container"

echo
echo "== 2) data persists in volume after container removed (new container reads D1)"
OUT2=$(printf '1\n\n8\n' | docker run -i --rm -v $VOL:/data $IMG 2>&1)
echo "$OUT2" | grep -E "D1 " | head -1
echo "$OUT2" | grep -qE "D1 +Docker Item +A +2 "; check $? "volume persistence (qty 2 after cut)"
docker run --rm -v $VOL:/data --entrypoint ls $IMG -la /data | tail -n +2
docker run --rm -v $VOL:/data --entrypoint sh $IMG -c 'test -f /data/inventory.db && test -f /data/low_stock_report.csv'; check $? "inventory.db + CSV written to /data"
docker run --rm -v $VOL:/data --entrypoint python $IMG -c "print(open('/data/low_stock_report.csv','rb').read(3)==b'\xef\xbb\xbf')" | grep -q True; check $? "CSV has UTF-8 BOM (BUG-106)"

echo
echo "== 3) --selftest"
docker run --rm -v $VOL:/data $IMG python -m inventory_app --selftest 2>&1 | tail -2
docker run --rm -v $VOL:/data $IMG python -m inventory_app --selftest >/dev/null 2>&1; check $? "--selftest exit 0"

echo
echo "== 4) image hardening"
U=$(docker run --rm --entrypoint id $IMG -u); echo "uid=$U"
[ "$U" = 1000 ]; check $? "runs as non-root (uid 1000)"
LEFT=$(docker run --rm --entrypoint sh $IMG -c 'find / -xdev \( -name "test_*.py" -path "*ENGSE*" -o -name app_v1.py -o -name conftest.py -o -name "*.whl" -path /tmp/\* \) 2>/dev/null; ls /src 2>/dev/null')
echo "leftover source/tests/wheel: ${LEFT:-none}"
[ -z "$LEFT" ]; check $? "no tests, app_v1.py, /src or wheel left in image"
docker run --rm --entrypoint python $IMG -c "import database_connection,os;print(os.path.isfile(os.path.join(os.path.dirname(database_connection.__file__),'schema.sql')))" | grep -q True; check $? "schema.sql installed next to database_connection.py"
docker run --rm --entrypoint python $IMG -c "import importlib.util as u;print(u.find_spec('pip') is None)" | grep -q True; check $? "pip removed from runtime image"

echo
echo "== 5) Trivy image scan (ต้องต่ออินเทอร์เน็ตเพื่อดาวน์โหลดฐานข้อมูลช่องโหว่)"
TRIVY="docker run --rm --network=host -v /var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache aquasec/trivy:0.67.2"
echo "-- all findings per target (รวมที่ยังไม่มีแพตช์จาก Debian)"
$TRIVY image --quiet --scanners vuln --format template --template '{{range .}}[{{.Target}}: {{len .Vulnerabilities}}] {{end}}' $IMG
echo "-- Python packages (library)"
$TRIVY image --quiet --scanners vuln --pkg-types library --exit-code 1 $IMG; check $? "Trivy: 0 vulnerabilities in Python packages"
echo "-- OS packages with a fix available (--ignore-unfixed)"
$TRIVY image --quiet --scanners vuln --pkg-types os --ignore-unfixed --exit-code 1 $IMG; check $? "Trivy: 0 fixable OS vulnerabilities"

docker volume rm $VOL >/dev/null
echo
echo "RESULT: $PASS passed, $FAIL failed"
[ $FAIL = 0 ] && echo "DOCKER IMAGE VERIFICATION: PASS" || echo "DOCKER IMAGE VERIFICATION: FAIL"
