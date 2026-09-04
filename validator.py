class Validator:
    @staticmethod
    def inputNonNegativeInt(prompt: str) -> int:
        """รับ input จนกว่าจะได้เลขจำนวนเต็มที่ไม่ติดลบ (int >= 0)"""
        while True:
            val_str = input(prompt).strip()
            try:
                val = int(val_str)
                if val < 0:
                    print("ข้อผิดพลาด: ค่าต้องเป็นจำนวนเต็มที่ไม่ติดลบ (>= 0) กรุณากรอกใหม่")
                    continue
                return val
            except ValueError:
                print("ข้อผิดพลาด: รูปแบบไม่ถูกต้อง กรุณากรอกเป็นตัวเลขจำนวนเต็ม")

    @staticmethod
    def inputNonNegativeFloat(prompt: str) -> float:
        """รับ input จนกว่าจะได้เลขทศนิยมที่ไม่ติดลบ (float >= 0.0)"""
        while True:
            val_str = input(prompt).strip()
            try:
                val = float(val_str)
                if val < 0.0:
                    print("ข้อผิดพลาด: ค่าต้องไม่ติดลบ (>= 0.0) กรุณากรอกใหม่")
                    continue
                return val
            except ValueError:
                print("ข้อผิดพลาด: รูปแบบไม่ถูกต้อง กรุณากรอกเป็นตัวเลขทศนิยม")

    @staticmethod
    def confirm(oldData: dict, newData: dict) -> bool:
        """แสดงเปรียบเทียบข้อมูลเดิมกับข้อมูลใหม่ แล้วให้ผู้ใช้กดยืนยัน (y/n)"""
        print("\n--- ยืนยันการเปลี่ยนแปลงข้อมูล ---")
        all_keys = set(list(oldData.keys()) + list(newData.keys()))
        for key in sorted(all_keys):
            old_val = oldData.get(key, "-")
            new_val = newData.get(key, "-")
            if old_val != new_val:
                print(f"  {key}: {old_val} -> {new_val}")
            else:
                print(f"  {key}: {old_val} (ไม่เปลี่ยน)")
        
        while True:
            ans = input("\nยืนยันการบันทึกทับข้อมูลหรือไม่? (y/n): ").strip().lower()
            if ans in ('y', 'yes'):
                return True
            elif ans in ('n', 'no'):
                return False
            print("กรุณาพิมพ์ 'y' เพื่อยืนยัน หรือ 'n' เพื่อยกเลิก")


# ============================================================
# ส่วนทดสอบ Definition of Done (DoD) สำหรับ SCRUM-9
# ============================================================
if __name__ == "__main__":
    import io
    import sys

    print("--- เริ่มการทดสอบ Definition of Done (SCRUM-9) ---")

    # 1. ทดสอบ inputNonNegativeInt (จำลอง input: 'abc' -> '-5' -> '10')
    sys.stdin = io.StringIO("abc\n-5\n10\n")
    res_int = Validator.inputNonNegativeInt("ใส่จำนวน: ")
    assert res_int == 10, f"FAILED: คาดหวัง 10 แต่ได้ {res_int}"
    print("✓ ผ่านเกณฑ์ 1: inputNonNegativeInt วนลูปจนกว่าจะได้ int >= 0")

    # 2. ทดสอบ inputNonNegativeFloat (จำลอง input: 'invalid' -> '-12.5' -> '25.50')
    sys.stdin = io.StringIO("invalid\n-12.5\n25.50\n")
    res_float = Validator.inputNonNegativeFloat("ใส่ราคา: ")
    assert res_float == 25.50, f"FAILED: คาดหวัง 25.50 แต่ได้ {res_float}"
    print("✓ ผ่านเกณฑ์ 2: inputNonNegativeFloat วนลูปจนกว่าจะได้ float >= 0.0")

    # 3. ทดสอบ confirm() กรณีตอบ Yes (จำลอง input: 'y')
    sys.stdin = io.StringIO("y\n")
    old_p = {"name": "Water", "quantity": 10, "price": 10.0}
    new_p = {"name": "Water", "quantity": 20, "price": 12.0}
    assert Validator.confirm(old_p, new_p) is True
    print("✓ ผ่านเกณฑ์ 3: confirm() คืนค่า True เมื่อผู้ใช้ตอบ 'y'")

    # 4. ทดสอบ confirm() กรณีตอบ No (จำลอง input: 'n')
    sys.stdin = io.StringIO("n\n")
    assert Validator.confirm(old_p, new_p) is False
    print("✓ ผ่านเกณฑ์ 4: confirm() คืนค่า False เมื่อผู้ใช้ตอบ 'n'")

    # คืนค่า stdin ปกติ
    sys.stdin = sys.__stdin__
    print("\nสรุป: ผ่านเกณฑ์ Definition of Done ของ SCRUM-9 ครบถ้วน 100%")