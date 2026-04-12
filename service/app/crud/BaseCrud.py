from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseCrud(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_by_page(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def get_all(self) -> List[ModelType]:
        return self.db.query(self.model).all()

    def create(self, obj_in: CreateSchemaType) -> ModelType:
        try:
            obj_in_data = obj_in.model_dump()
            db_obj = self.model(**obj_in_data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
        except Exception as e:
            self.db.rollback()
            raise e
        return db_obj

    def update(
        self,
        id: int,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        try:
            db_obj = self.db.get(self.model, id)
            if db_obj is None:
                raise RuntimeError("Object not found")
            
            obj_data = obj_in.model_dump(exclude_unset=True) if isinstance(obj_in, BaseModel) else obj_in
            for field, value in obj_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            self.db.commit()
            self.db.refresh(db_obj)
        except Exception as e:
            self.db.rollback()
            raise e
        return db_obj

    def remove(self, id: int) -> Optional[ModelType]:
        try:
            obj = self.db.get(self.model, id)
            if obj is None:
                return None
            self.db.delete(obj)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        return obj
