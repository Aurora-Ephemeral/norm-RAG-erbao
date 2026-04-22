import logging

from app.core.celery import celery_app
from app.core.minIO import minio_client
from app.crud.FileCrud import FileCrud
from app.db.Postgresql import SessionLocal
from app.domain.file.model import ParseStatusEnum
from app.domain.file.parse import parse_pdf
from app.domain.file.schemas import RawFileUpdate

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="split_file_to_chunk")
def split_file_to_chunk(self, file_id: str, document_id: str):
    pass


@celery_app.task(bind=True, name="parse_pdf_task", max_retries=3, default_retry_delay=30)
def parse_pdf_task(self, file_id: str):
    db = SessionLocal()
    fid = int(file_id)
    try:
        crud = FileCrud(db)

        raw_file = crud.get(fid)
        if raw_file is None:
            raise ValueError(f"File {file_id} not found")

        crud.update(fid, RawFileUpdate(parse_status=ParseStatusEnum.PROCESSING))

        pdf_bytes = minio_client.download_bytes(raw_file.storage_path)
        result = parse_pdf(pdf_bytes)

        existing_meta = raw_file.metadata_json or {}
        crud.update(fid, RawFileUpdate(
            parse_status=ParseStatusEnum.DONE,
            metadata_json={**existing_meta, **result.metadata},
        ))

        logger.info("parse_pdf_task done: file_id=%s elements=%d", fid, len(result.elements))
        return {"file_id": fid, "element_count": len(result.elements)}

    except Exception as exc:
        if self.request.retries >= self.max_retries:
            FileCrud(db).update(fid, RawFileUpdate(
                parse_status=ParseStatusEnum.FAILED,
                error_message=str(exc),
            ))
            logger.error("parse_pdf_task permanently failed: file_id=%s error=%s", file_id, exc)
        raise self.retry(exc=exc)

    finally:
        db.close()