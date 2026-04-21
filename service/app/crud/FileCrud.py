import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.crud.BaseCrud import BaseCrud
from app.domain.file.model import RawFile
from app.domain.file.schemas import RawFileCreate, RawFileUpdate


class FileCrud(BaseCrud[RawFile, RawFileCreate, RawFileUpdate]):
    def __init__(self, db: Session):
        super().__init__(RawFile, db)

    def get_by_uuid(self, file_uuid: uuid.UUID) -> Optional[RawFile]:
        return self.db.query(RawFile).filter(RawFile.file_uuid == file_uuid).first()

    def get_by_md5(self, file_md5: str) -> Optional[RawFile]:
        return self.db.query(RawFile).filter(RawFile.file_md5 == file_md5).first()

    def soft_delete(self, id: int) -> Optional[RawFile]:
        return self.update(id, RawFileUpdate(is_deleted=True))
