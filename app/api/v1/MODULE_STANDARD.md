WellPlus API Module Standard (Production Architecture)

Version: 1.0
Scope: All modules under app/api/v1/modules/*

🎯 Purpose

เอกสารนี้กำหนดมาตรฐานโครงสร้าง module สำหรับ WellPlus เพื่อให้:

ลด Circular Import

ลด Schema/DTO สับสน

ทำ Response ให้เป็นมาตรฐานเดียวกันทั้งระบบ

รองรับ Clean Architecture

Maintain ได้ง่ายในระยะยาว

1️⃣ Standard Folder Structure

ทุก module ต้องใช้โครงสร้างนี้:

app/api/v1/modules/<module>/
  __init__.py
  dependencies.py

  routers/
    __init__.py
    <entity>_router.py
    <entity>_read_router.py
    <entity>_search_router.py

  services/
    __init__.py
    <entity>_service.py
    <entity>_read_service.py
    <entity>_search_service.py

  repositories/
    __init__.py
    <entity>_repository.py
    <entity>_read_repository.py
    <entity>_search_repository.py

  models/
    __init__.py
    dtos.py
    schemas.py
    orm.py                # optional
    _envelopes/
      __init__.py
      <module>_envelopes.py
2️⃣ Models Layer Rules
2.1 schemas.py

ใช้สำหรับ Request Models (Inbound) เท่านั้น

ตัวอย่าง:

CreateRequest

UpdateRequest

SearchFilterRequest

❌ ห้ามใส่ Response DTO ในไฟล์นี้

2.2 dtos.py

ใช้สำหรับ Response Models (Outbound) เท่านั้น

ตัวอย่าง:

XItemDTO

XSearchItemDTO

XDetailDTO

Payload models ที่ใช้ส่งออก

❌ ห้ามใส่ Request model ในไฟล์นี้

2.3 _envelopes/

ใช้สำหรับผูก response_model กับ Envelope กลาง

ตัวอย่าง:

XSearchEnvelope = SuccessEnvelope[ListPayload[XDTO]]
XGetEnvelope = SuccessEnvelope[dict]

ต้องอยู่ที่:

models/_envelopes/

❌ ห้ามมีทั้ง _envelopes/ และ envelopes/ ซ้ำกัน

3️⃣ Response Standard
3.1 Search / List

ทุก endpoint ที่เป็น /search หรือ list ต้องคืนรูปแบบนี้:

{
  "status": "success",
  "data": {
    "filters": {...},
    "paging": {
      "total": 0,
      "limit": 50,
      "offset": 0
    },
    "items": [ ... ]
  }
}

กฎ:

ใช้ ListPayload[T]

key ต้องเป็น "items" เสมอ

ห้ามใช้ "companies", "rooms", "users" ฯลฯ

3.2 Single Item (GET by id / POST / PUT)

ต้องคืน:

{
  "data": {
    "item": { ... }
  }
}

key ต้องเป็น "item" เสมอ

4️⃣ Router Rules
4.1 Router Naming
Type	File
Search	<entity>_search_router.py
Read (by id)	<entity>_read_router.py
Create/Update/Delete	<entity>_router.py
4.2 Facade Router (routers/init.py)

ต้องเป็นรูปแบบนี้:

router = APIRouter(prefix="/module", tags=["Module"])

router.include_router(entity_search_router)
router.include_router(entity_read_router)
router.include_router(entity_router)

❌ ห้าม import router จาก package ตัวเอง (จะเกิด circular import)

5️⃣ Service Rules

Service ทำ Business Logic เท่านั้น

ห้ามเขียน SQL ใน service

ห้าม return ORM object สำหรับ search/list

Service ต้องเรียก repository เท่านั้น

6️⃣ Repository Rules
6.1 Search Repository

ต้องใช้:

stmt = select(columns...)
rows = (await session.execute(stmt)).mappings().all()

✅ ต้องคืน dict-like rows
❌ ห้ามคืน ORM object สำหรับ list/search

6.2 Read Repository

สามารถคืน ORM object ได้

ต้อง eager load relation ที่จำเป็น

หรือ map เป็น dict ก่อน return

7️⃣ Pagination Standard

ทุก search ต้องรองรับ:

q (optional)

limit (default 50)

offset (default 0)

และคืน:

paging: {
  total,
  limit,
  offset
}
8️⃣ Import Policy

Router import:

Request → from models.schemas

Response → from models.dtos

Envelope → from models._envelopes

❌ ห้าม import Request จาก dtos
❌ ห้าม import Response จาก schemas

9️⃣ Global Helper

Search router ต้องใช้:

build_list_payload()

ห้ามสร้าง paging JSON เอง

🔟 Done Checklist (ก่อน Merge)

 ใช้ models/ อย่างเดียว (ไม่มี schemas/ แยก)

 มี _envelopes/ ที่เดียว

 Search คืน items

 Single คืน item

 Search repo ใช้ .mappings()

 routers/init.py ไม่มี circular import

🏁 Golden Rule

"Every module must look identical in structure to masters."

Consistency > Creativity