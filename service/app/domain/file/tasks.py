import logging

from app.core.celery import celery_app
from app.core.config import settings
from app.core.minIO import minio_client
from app.crud.ChunkCrud import ChunkCrud
from app.crud.DocumentCrud import DocumentCrud
from app.crud.FileCrud import FileCrud
from app.db.Postgresql import SessionLocal
from app.domain.chunk.schemas import ChunkCreate
from app.domain.document.model import DocStatusEnum
from app.domain.document.schemas import DocumentUpdate
from app.domain.file.embedding import embed_document
from app.domain.file.parse import parse_pdf
from app.domain.file.schemas import RawFileUpdate
from app.domain.file.split_chunks import split_chunks

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="processing_document_task", max_retries=3, default_retry_delay=30)
def processing_document_task(self, file_id: str, document_id: str):
    db = SessionLocal()
    fid = int(file_id)
    did = int(document_id)
    try:
        file_crud = FileCrud(db)
        doc_crud = DocumentCrud(db)
        chunk_crud = ChunkCrud(db)

        raw_file = file_crud.get(fid)
        if raw_file is None:
            raise ValueError(f"File {file_id} not found")

        doc_crud.update(did, DocumentUpdate(doc_status=DocStatusEnum.PROCESSING))

        pdf_bytes = minio_client.download_bytes(raw_file.storage_path)
        parse_result = parse_pdf(pdf_bytes)
        chunks = split_chunks(parse_result)

        chunk_creates = [
            ChunkCreate(
                document_id=did,
                chunk_index=i,
                chunk_text=c.text,
                token_count=len(c.text) // 4,
                char_count=len(c.text),
                embedding_model=settings.embedding_model,
                page_no=c.page,
                section_title=c.section_path[-1] if c.section_path else None,
                metadata_json={
                    "chunk_type": c.chunk_type,
                    "section_path": c.section_path,
                    "referenced_standards": c.referenced_standards,
                    "rows": c.rows,
                    "footnotes": c.footnotes,
                },
            )
            for i, c in enumerate(chunks)
        ]
        chunk_crud.bulk_create(chunk_creates)

        existing_meta = raw_file.metadata_json or {}
        file_crud.update(fid, RawFileUpdate(
            metadata_json={**existing_meta, **parse_result.metadata},
        ))
        doc_crud.update(did, DocumentUpdate(chunk_count=len(chunks)))
        logger.info("processing_document_task done: file_id=%s chunks=%d", fid, len(chunks))

        embed_document_task.delay(document_id)
        return {"file_id": fid, "chunk_count": len(chunks)}

    except Exception as exc:
        if self.request.retries >= self.max_retries:
            DocumentCrud(db).update(did, DocumentUpdate(
                doc_status=DocStatusEnum.FAILED,
                metadata_json={"error": str(exc)},
            ))
            logger.error("processing_document_task permanently failed: file_id=%s error=%s", fid, exc)
            raise exc
        raise self.retry(exc=exc)

    finally:
        db.close()


@celery_app.task(bind=True, name="embed_document_task", max_retries=3, default_retry_delay=60)
def embed_document_task(self, document_id: str):
    db = SessionLocal()
    did = int(document_id)
    try:
        doc_crud = DocumentCrud(db)
        chunk_crud = ChunkCrud(db)

        chunks = chunk_crud.get_unembedded(did)
        if not chunks:
            logger.info("embed_document_task: no unembedded chunks for document_id=%s", did)
            doc_crud.update(did, DocumentUpdate(doc_status=DocStatusEnum.ACTIVE))
            return {"document_id": did, "embedded": 0}

        updates = embed_document(chunks)
        chunk_crud.bulk_update_embeddings(updates)

        doc_crud.update(did, DocumentUpdate(doc_status=DocStatusEnum.ACTIVE))
        logger.info("embed_document_task done: document_id=%s embedded=%d", did, len(updates))
        return {"document_id": did, "embedded": len(updates)}

    except Exception as exc:
        if self.request.retries >= self.max_retries:
            DocumentCrud(db).update(did, DocumentUpdate(
                doc_status=DocStatusEnum.FAILED,
                metadata_json={"error": str(exc)},
            ))
            logger.error("embed_document_task permanently failed: document_id=%s error=%s", did, exc)
            raise exc
        raise self.retry(exc=exc)

    finally:
        db.close()
