# Risk Register — ระบบสินค้าคงคลัง (app_v1.py)

<table>
<tr>
<th>ความเสี่ยงที่ระบุ</th>
<th>ระดับดั้งเดิม</th>
<th>แผนรับมือ/ป้องกัน (Mitigation Plan)</th>
<th>ระดับที่เหลืออยู่</th>
</tr>

<tr>
<td>ข้อมูลใน data.json อาจเสียหายหรือหายทั้งหมด เมื่อเกิดข้อผิดพลาดระหว่างบันทึกไฟล์</td>
<td align="center"><span style="background-color:#f8b4b4; color:#c0392b; padding:2px 10px; border-radius:8px; font-weight:bold;">สูงมาก</span></td>
<td>เปลี่ยนวิธีบันทึกโดยเขียนลงไฟล์ชั่วคราวก่อน แล้วค่อยเปลี่ยนชื่อไฟล์ (Atomic Write)</td>
<td align="center"><span style="background-color:#b7e4c7; color:#1b7a3d; padding:2px 10px; border-radius:8px; font-weight:bold;">ต่ำ</span></td>
</tr>

<tr>
<td>โปรแกรมหยุดทำงานทันทีเมื่อผู้ใช้กรอกข้อมูลที่ไม่ใช่ตัวเลข</td>
<td align="center"><span style="background-color:#f8b4b4; color:#c0392b; padding:2px 10px; border-radius:8px; font-weight:bold;">สูงมาก</span></td>
<td>เพิ่มระบบตรวจสอบข้อมูลก่อนประมวลผล และแจ้งให้ผู้ใช้กรอกใหม่</td>
<td align="center"><span style="background-color:#b7e4c7; color:#1b7a3d; padding:2px 10px; border-radius:8px; font-weight:bold;">ต่ำ</span></td>
</tr>

<tr>
<td>หากเปิดโปรแกรม 2 หน้าต่างพร้อมกัน ข้อมูลอาจชนกันและเสียหาย</td>
<td align="center"><span style="background-color:#f8b4b4; color:#c0392b; padding:2px 10px; border-radius:8px; font-weight:bold;">สูงมาก</span></td>
<td>เปลี่ยนไปใช้ฐานข้อมูล SQLite ที่รองรับการใช้งานพร้อมกัน</td>
<td align="center"><span style="background-color:#f6e2a3; color:#8a6d1d; padding:2px 10px; border-radius:8px; font-weight:bold;">ปานกลาง</span></td>
</tr>

<tr>
<td>กดแก้ไขสินค้าโดยไม่ตั้งใจ ระบบเขียนทับข้อมูลเดิมทันทีโดยไม่มีการถามยืนยัน</td>
<td align="center"><span style="background-color:#f9cfa0; color:#b8600a; padding:2px 10px; border-radius:8px; font-weight:bold;">สูง</span></td>
<td>เพิ่มขั้นตอนยืนยันก่อนบันทึก โดยแสดงข้อมูลเดิมเปรียบเทียบ</td>
<td align="center"><span style="background-color:#b7e4c7; color:#1b7a3d; padding:2px 10px; border-radius:8px; font-weight:bold;">ต่ำ</span></td>
</tr>

<tr>
<td>ผู้ใช้สามารถกรอกจำนวนสินค้าหรือราคาเป็นตัวเลขติดลบได้</td>
<td align="center"><span style="background-color:#f9cfa0; color:#b8600a; padding:2px 10px; border-radius:8px; font-weight:bold;">สูง</span></td>
<td>เพิ่มการตรวจสอบว่าตัวเลขต้องมากกว่าหรือเท่ากับ 0 ก่อนบันทึก</td>
<td align="center"><span style="background-color:#b7e4c7; color:#1b7a3d; padding:2px 10px; border-radius:8px; font-weight:bold;">ต่ำ</span></td>
</tr>

<tr>
<td>สต็อกสินค้าอาจติดลบได้หากมีการตัดสต็อกพร้อมกัน</td>
<td align="center"><span style="background-color:#f9cfa0; color:#b8600a; padding:2px 10px; border-radius:8px; font-weight:bold;">สูง</span></td>
<td>ตรวจสอบยอดสต็อกอีกครั้งหลังคำนวณ และกำหนดค่าขั้นต่ำไว้ที่ 0</td>
<td align="center"><span style="background-color:#b7e4c7; color:#1b7a3d; padding:2px 10px; border-radius:8px; font-weight:bold;">ต่ำ</span></td>
</tr>

<tr>
<td>ไฟล์ข้อมูลอาจถูกสร้างผิดตำแหน่งขึ้นอยู่กับโฟลเดอร์ที่เปิดโปรแกรม</td>
<td align="center"><span style="background-color:#f6e2a3; color:#8a6d1d; padding:2px 10px; border-radius:8px; font-weight:bold;">ปานกลาง</span></td>
<td>กำหนดที่เก็บไฟล์ให้อยู่โฟลเดอร์เดียวกับโปรแกรมเสมอ</td>
<td align="center"><span style="background-color:#b7e4c7; color:#1b7a3d; padding:2px 10px; border-radius:8px; font-weight:bold;">ต่ำ</span></td>
</tr>

<tr>
<td>ไม่มีประวัติบันทึกว่าใครเปลี่ยนข้อมูลอะไรเมื่อไหร่</td>
<td align="center"><span style="background-color:#f6e2a3; color:#8a6d1d; padding:2px 10px; border-radius:8px; font-weight:bold;">ปานกลาง</span></td>
<td>เพิ่มระบบบันทึก Log อัตโนมัติทุกครั้งที่มีการเปลี่ยนแปลงข้อมูล</td>
<td align="center"><span style="background-color:#b7e4c7; color:#1b7a3d; padding:2px 10px; border-radius:8px; font-weight:bold;">ต่ำ</span></td>
</tr>

<tr>
<td>ชื่อสินค้าภาษาไทยอาจแสดงผลเป็นตัวอักษรแปลกๆ บนคอมพิวเตอร์ต่างรุ่น</td>
<td align="center"><span style="background-color:#f6e2a3; color:#8a6d1d; padding:2px 10px; border-radius:8px; font-weight:bold;">ปานกลาง</span></td>
<td>กำหนดรหัสภาษา UTF-8 ในทุกจุดอ่านหรือเขียนไฟล์</td>
<td align="center"><span style="background-color:#b7e4c7; color:#1b7a3d; padding:2px 10px; border-radius:8px; font-weight:bold;">ต่ำ</span></td>
</tr>

<tr>
<td>โค้ดส่วนเพิ่มและแก้ไขสินค้าซ้ำกัน อาจทำให้ระบบทำงานไม่สมเหตุสมผล</td>
<td align="center"><span style="background-color:#f6e2a3; color:#8a6d1d; padding:2px 10px; border-radius:8px; font-weight:bold;">ปานกลาง</span></td>
<td>รวมโค้ดซ้ำให้เหลือจุดเดียว และเขียน Unit Test</td>
<td align="center"><span style="background-color:#b7e4c7; color:#1b7a3d; padding:2px 10px; border-radius:8px; font-weight:bold;">ต่ำ</span></td>
</tr>

<tr>
<td>ชื่อตัวแปรสั้นและไม่สื่อความหมาย ทำให้อ่านและแก้ไขโค้ดได้ยาก</td>
<td align="center"><span style="background-color:#b7e4c7; color:#1b7a3d; padding:2px 10px; border-radius:8px; font-weight:bold;">ต่ำ</span></td>
<td>เปลี่ยนชื่อตัวแปรให้อ่านเข้าใจง่าย เช่น x → inventory</td>
<td align="center"><span style="background-color:#b7e4c7; color:#1b7a3d; padding:2px 10px; border-radius:8px; font-weight:bold;">ต่ำ</span></td>
</tr>

<tr>
<td>หากมีสินค้าจำนวนมาก การแสดงผลทั้งหมดในครั้งเดียวอาจทำให้ผลลัพธ์ท่วมหน้าจอ</td>
<td align="center"><span style="background-color:#b7e4c7; color:#1b7a3d; padding:2px 10px; border-radius:8px; font-weight:bold;">ต่ำ</span></td>
<td>เพิ่มระบบแสดงผลทีละหน้า หรือฟังก์ชันค้นหา</td>
<td align="center"><span style="background-color:#b7e4c7; color:#1b7a3d; padding:2px 10px; border-radius:8px; font-weight:bold;">ต่ำ</span></td>
</tr>

</table>
