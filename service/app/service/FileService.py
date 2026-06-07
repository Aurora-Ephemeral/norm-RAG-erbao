from pathlib import Path
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.crud.FileCrud import FileCrud
from app.crud.DocumentCrud import DocumentCrud
from app.crud.KnowledgeBaseCrud import KnowledgeBaseCrud
from app.domain.file.md5 import Md5Utils
from app.domain.document.schemas import DocumentCreate
from app.domain.file.schemas import RawFile, RawFileCreate, RawFileUploadResult
from app.domain.file.tasks import processing_document_task
from app.core.minIO import MinIOClient, UploadResult
class FileService:
    def __init__(self, db: Session, minio: MinIOClient):
        self.db = db
        self.crud = FileCrud(db)
        self.crud_doc = DocumentCrud(db)
        self.crud_kb = KnowledgeBaseCrud(db)
        self.minio = minio
    _MAX_FILE_SIZE = 20 * 1024 * 1024
    _ALLOWED_EXT = {"pdf"}

    def _validate_file(self, file: UploadFile) -> None:
        file_ext = Path(file.filename).suffix.lstrip(".").lower()
        if file_ext not in self._ALLOWED_EXT:
            raise HTTPException(status_code=415, detail=f"Unsupported file type: {file_ext}. Only PDF is allowed.")
        if file.size is None or file.size > self._MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"File too large: {file.size} bytes. Maximum allowed size is 20MB.")

    async def upload_file(
            self, 
            file: UploadFile, 
            knowledge_base_id:int,
            file_name:str,
            part_type:str,
            standard_no: str
        ) -> RawFileUploadResult:
        # 0. validate file type and size
        self._validate_file(file)

        # 1. check if file is already in database
        file_md5 = await Md5Utils.calculate_md5(file)
        fetch_file = self.crud.get_by_md5(file_md5)
        # 2. if file is already in database, return info message
        if fetch_file is not None:
            # 2.1 check if file is related to current knowledge base
            fetch_doc = self.crud_doc.get_by_kb_id_and_file_id(knowledge_base_id, fetch_file.id)
            if fetch_doc is not None:
                return RawFileUploadResult(
                    file_exist = True,
                    doc_exist = True,
                    data=RawFile.model_validate(fetch_file)
                )
            else:
                #2.2 add file as a new doc to current knowledge base
                db_doc = self.crud_doc.create(DocumentCreate(
                    file_id=fetch_file.id,
                    knowledge_base_id=knowledge_base_id,
                    doc_title=fetch_file.file_name,
                    part_type=part_type,
                    standard_no=standard_no,
                ))
                # 2.3 trigger async parse + chunk pipeline
                processing_document_task.delay(str(db_file.id), str(db_doc.id))

                return RawFileUploadResult(
                    file_exist = True,
                    doc_exist = False,
                    data=RawFile.model_validate(fetch_file)
                )
        # 3. if not, upload it to minIO storage 
        upload_result:UploadResult = await self.minio.upload(file)
        # 4. save file info to databse
        try:
            db_file = self.crud.create(RawFileCreate(
                file_md5=file_md5,
                file_name=file_name if file_name else file.filename,
                file_ext=Path(file.filename).suffix.lstrip("."),
                mime_type=file.content_type,
                file_size=file.size,
                storage_path=upload_result.storage_path,
            ))

            # 5. save document info to database
            db_doc = self.crud_doc.create(DocumentCreate(
                file_id=db_file.id,
                knowledge_base_id=knowledge_base_id,
                doc_title=file_name if file_name else file.filename,
                part_type=part_type,
                standard_no=standard_no,
            ))
            # 6. atomically increment KB document counter
            self.crud_kb.increment_document_count(knowledge_base_id)
        except Exception as e:
            await self.minio.delete(upload_result.storage_path)
            raise e

        # 7. trigger async parse + chunk pipeline
        processing_document_task.delay(str(db_file.id), str(db_doc.id))

        return RawFileUploadResult(
            file_exist = False,
            doc_exist = False,
            data=RawFile.model_validate(db_file)
        )

        

