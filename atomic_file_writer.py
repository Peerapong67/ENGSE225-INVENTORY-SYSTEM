"""
AtomicFileWriter
=================
ลดความเสี่ยงตาม Risk Register (risk_register_app_v1_emoji.md):
"ข้อมูลใน data.json อาจเสียหายหรือหายทั้งหมด เมื่อเกิดข้อผิดพลาดระหว่างบันทึกไฟล์"

ปัญหาของ open(path, 'w') ตรงๆ คือไฟล์เดิมถูกล้างทิ้งทันทีที่เปิด ถ้าโปรแกรมพัง/
ไฟดับระหว่างเขียน จะเหลือไฟล์ว่างหรือข้อมูลครึ่งเดียว

หลักการ Atomic Write:
1. เขียนข้อมูลลงไฟล์ชั่วคราว (.tmp) ในโฟลเดอร์เดียวกับไฟล์ปลายทาง
2. flush + fsync ให้ข้อมูลลงดิสก์จริงก่อน
3. os.replace() สลับไฟล์ชั่วคราวเข้าแทนไฟล์จริงในขั้นตอนเดียว (atomic ทั้ง
   Windows และ POSIX) — ผู้อ่านจะเห็นแค่ไฟล์เก่าครบๆ หรือไฟล์ใหม่ครบๆ เท่านั้น
4. ถ้าเกิด error ระหว่างทาง ลบไฟล์ชั่วคราวทิ้ง ไฟล์เดิมยังอยู่ครบไม่ถูกแตะ
"""

import os
import tempfile
from typing import Callable, IO, Optional


class AtomicFileWriter:
    """เขียนไฟล์แบบ all-or-nothing: สำเร็จทั้งไฟล์ หรือไฟล์เดิมไม่เปลี่ยนเลย"""

    @staticmethod
    def write(path: str, write_fn: Callable[[IO], None],
              encoding: str = "utf-8", newline: Optional[str] = None) -> None:
        """เขียนไฟล์ path แบบ atomic โดยให้ write_fn เป็นผู้เขียนเนื้อหาลง file object

        Args:
            path: path ปลายทางของไฟล์ที่ต้องการบันทึก
            write_fn: ฟังก์ชันที่รับ file object (เปิดโหมดเขียน text) แล้วเขียนเนื้อหาลงไป
            encoding: encoding ของไฟล์ (ค่าเริ่มต้น utf-8 รองรับภาษาไทย)
            newline: ส่งต่อให้ open() เช่น '' สำหรับไฟล์ CSV

        Raises:
            Exception ใดๆ ที่ write_fn หรือการเขียนไฟล์โยนออกมา (ไฟล์เดิมยังอยู่ครบ)
        """
        # ไฟล์ชั่วคราวต้องอยู่โฟลเดอร์เดียวกับปลายทาง เพราะ os.replace() จะ atomic
        # ได้ก็ต่อเมื่ออยู่บน filesystem/drive เดียวกันเท่านั้น
        dir_name = os.path.dirname(os.path.abspath(path))
        fd, tmp_path = tempfile.mkstemp(
            dir=dir_name, prefix=os.path.basename(path) + ".", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding=encoding, newline=newline) as f:
                write_fn(f)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, path)
        except BaseException:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise
