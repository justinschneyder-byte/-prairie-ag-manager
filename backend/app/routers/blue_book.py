"""
Storage and serving for the farm's own uploaded Blue Book (Alberta Crop
Protection Guide) PDF. We never extract, parse, or reproduce its content —
it's copyrighted material. This is purely "store Justin's own file so he can
open it in the app," the same as it sitting on his phone, just filed
alongside everything else. One document per farm; a new upload replaces the
previous file and row.
"""

import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .. import models
from ..config import get_settings
from ..database import get_db
from ..farm import get_current_farm_id

router = APIRouter(prefix="/blue-book", tags=["blue-book"])
settings = get_settings()

CHUNK_SIZE = 1024 * 1024  # 1 MB


def _storage_dir() -> Path:
    d = Path(settings.blue_book_storage_dir)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _stored_path(farm_id: int) -> Path:
    return _storage_dir() / f"farm-{farm_id}.pdf"


@router.get("")
def get_blue_book_meta(farm_id: int = Depends(get_current_farm_id), db: Session = Depends(get_db)):
    doc = db.query(models.BlueBookDocument).filter(models.BlueBookDocument.farm_id == farm_id).first()
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Blue Book uploaded yet.")
    return {
        "filename": doc.original_filename,
        "size_bytes": doc.size_bytes,
        "uploaded_at": doc.uploaded_at,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_blue_book(
    file: UploadFile = File(...),
    farm_id: int = Depends(get_current_farm_id),
    db: Session = Depends(get_db),
):
    is_pdf_name = (file.filename or "").lower().endswith(".pdf")
    is_pdf_type = file.content_type in ("application/pdf", "application/octet-stream")
    if not (is_pdf_name and is_pdf_type):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are accepted.")

    max_bytes = settings.blue_book_max_size_mb * 1024 * 1024
    dest_path = _stored_path(farm_id)
    tmp_path = dest_path.with_suffix(".pdf.tmp")

    size = 0
    too_large = False
    with open(tmp_path, "wb") as out:
        while chunk := await file.read(CHUNK_SIZE):
            size += len(chunk)
            if size > max_bytes:
                too_large = True
                break
            out.write(chunk)
    await file.close()

    if too_large:
        tmp_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"That PDF is larger than the {settings.blue_book_max_size_mb} MB limit. "
            "Try re-saving/compressing it, or ask to raise the limit.",
        )

    tmp_path.replace(dest_path)

    doc = db.query(models.BlueBookDocument).filter(models.BlueBookDocument.farm_id == farm_id).first()
    if doc is None:
        doc = models.BlueBookDocument(
            farm_id=farm_id,
            original_filename=file.filename,
            stored_path=str(dest_path),
            size_bytes=size,
        )
        db.add(doc)
    else:
        doc.original_filename = file.filename
        doc.stored_path = str(dest_path)
        doc.size_bytes = size
        doc.uploaded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(doc)

    return {
        "filename": doc.original_filename,
        "size_bytes": doc.size_bytes,
        "uploaded_at": doc.uploaded_at,
    }


@router.get("/file")
def get_blue_book_file(farm_id: int = Depends(get_current_farm_id), db: Session = Depends(get_db)):
    doc = db.query(models.BlueBookDocument).filter(models.BlueBookDocument.farm_id == farm_id).first()
    if doc is None or not os.path.exists(doc.stored_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Blue Book uploaded yet.")
    return FileResponse(
        doc.stored_path,
        media_type="application/pdf",
        filename=doc.original_filename,
        content_disposition_type="inline",
    )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_blue_book(farm_id: int = Depends(get_current_farm_id), db: Session = Depends(get_db)):
    doc = db.query(models.BlueBookDocument).filter(models.BlueBookDocument.farm_id == farm_id).first()
    if doc is None:
        return None
    if os.path.exists(doc.stored_path):
        os.remove(doc.stored_path)
    db.delete(doc)
    db.commit()
    return None
