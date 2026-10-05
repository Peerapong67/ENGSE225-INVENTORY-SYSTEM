# ============================================================
# Inventory Management System v2.0.1 - Container image
#
# build:  docker build -t engse225-inventory-system:2.0.1 .
# run:    docker run -it --rm -v inventory-data:/data engse225-inventory-system:2.0.1
#
# - stage 1 สร้าง wheel จากซอร์ส (pip wheel ใช้ build backend hatchling ตาม pyproject.toml)
# - stage 2 ติดตั้งเฉพาะ wheel ลง image ที่ไม่มีซอร์สโค้ด เทสต์ หรือ pip และรันด้วยผู้ใช้ที่ไม่ใช่ root
# - ตรวจ image หลัง build: sh scripts/verify_docker.sh
# - inventory.db และไฟล์ CSV ถูกสร้างใน /data (current working directory) ให้ mount volume
#   ไว้ที่ /data เพื่อไม่ให้ข้อมูลหายเมื่อลบ container
# - โปรแกรมเป็นเมนูแบบ interactive ต้องรันด้วย -it
# ============================================================
FROM python:3.12-slim AS build
WORKDIR /src
COPY pyproject.toml README.md schema.sql ./
COPY inventory_app.py validator.py product.py product_repository.py database_connection.py \
     logger.py csv_report_exporter.py atomic_file_writer.py ./
RUN pip wheel --no-cache-dir --disable-pip-version-check --no-deps --wheel-dir /dist .

FROM python:3.12-slim
LABEL org.opencontainers.image.title="engse225-inventory-system" \
      org.opencontainers.image.version="2.0.1" \
      org.opencontainers.image.source="https://github.com/Peerapong67/ENGSE225-INVENTORY-SYSTEM"
ENV PYTHONIOENCODING=utf-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
# ติดตั้ง security update ของ Debian ที่ออกหลัง base image ถูกสร้าง (Trivy พบ libpcre2 ที่มีแพตช์แล้ว)
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
COPY --from=build /dist/*.whl /tmp/
# ติดตั้ง wheel แล้วถอน pip ออก: โปรแกรมไม่ใช้ pip ตอนรัน และ Trivy พบช่องโหว่ใน urllib3/msgpack
# ที่ pip ฝังมาใน pip/_vendor (pip-audit ไม่ตรวจส่วนนี้) รวมถึง CVE-2026-13346 ของ pip เอง
RUN pip install --no-cache-dir --disable-pip-version-check /tmp/*.whl \
    && pip uninstall -y --disable-pip-version-check pip \
    && rm -f /tmp/*.whl \
    && useradd --create-home --uid 1000 app \
    && mkdir /data \
    && chown app:app /data
USER app
WORKDIR /data
VOLUME ["/data"]
CMD ["python", "-m", "inventory_app"]
