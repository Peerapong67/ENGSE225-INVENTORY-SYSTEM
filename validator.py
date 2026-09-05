class Validator:
    """
    ตรงกับ class Validator ใน UML diagram — เมธอด static ทั้งหมด
    InventoryApp เรียกใช้แทนการเช็ค input เอง
    """

    @staticmethod
    def inputNonNegativeInt(prompt: str) -> int:
        """รับ input จาก console วนซ้ำจนกว่าจะได้เลขจำนวนเต็มที่ไม่ติดลบ

        Args:
            prompt: ข้อความที่แสดงตอนถาม input (ส่งต่อให้ input())

        Returns:
            จำนวนเต็มที่ผู้ใช้กรอก ซึ่งรับประกันว่า >= 0 เสมอ
        """
        while True:
            raw = input(prompt)
            try:
                value = int(raw)
            except ValueError:
                print("กรุณากรอกจำนวนเต็มเท่านั้น")
                continue
            if value < 0:
                print("ค่าต้องไม่ติดลบ กรุณากรอกใหม่")
                continue
            return value

    @staticmethod
    def inputNonNegativeFloat(prompt: str) -> float:
        """รับ input จาก console วนซ้ำจนกว่าจะได้เลขทศนิยมที่ไม่ติดลบ

        Args:
            prompt: ข้อความที่แสดงตอนถาม input (ส่งต่อให้ input())

        Returns:
            เลขทศนิยมที่ผู้ใช้กรอก ซึ่งรับประกันว่า >= 0 เสมอ
        """
        while True:
            raw = input(prompt)
            try:
                value = float(raw)
            except ValueError:
                print("กรุณากรอกตัวเลขเท่านั้น")
                continue
            if value < 0:
                print("ค่าต้องไม่ติดลบ กรุณากรอกใหม่")
                continue
            return value

    @staticmethod
    def confirm(oldData: dict, newData: dict) -> bool:
        """แสดงข้อมูลเดิมเทียบกับข้อมูลใหม่ แล้วให้ผู้ใช้ยืนยันก่อนบันทึกทับ

        Args:
            oldData: ข้อมูลชุดเดิมที่จะถูกเขียนทับ (แสดงให้ผู้ใช้ดูก่อนตัดสินใจ)
            newData: ข้อมูลชุดใหม่ที่จะถูกบันทึกถ้าผู้ใช้ยืนยัน

        Returns:
            True ถ้าผู้ใช้พิมพ์ "y"/"Y" เพื่อยืนยัน, False ในทุกกรณีอื่น
        """
        print("ข้อมูลเดิม:", oldData)
        print("ข้อมูลใหม่:", newData)
        answer = input("ยืนยันบันทึกทับข้อมูลเดิม? (y/n): ").strip().lower()
        return answer == "y"
