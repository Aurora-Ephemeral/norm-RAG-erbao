from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import String
from app.domain.common.schemas import PageResult
import math

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseCrud(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_by_page(self, current: int = 0, size: int = 100, filter_obj: Optional[Dict[str, Any]] = None) -> PageResult[ModelType]:
        if filter_obj is None:
            filter_obj = {}
        total = self.db.query(self.model).count()
        # calculate the maximum number of pages
        max_page = max(1, math.ceil(total / size))
        current = min(current, max_page)
        query = self._apply_filter(self.db.query(self.model), filter_obj)
        rows = query.offset((current - 1) * size).limit(size).all()
        return PageResult(total=total, rows=rows, current=current, size=size)

    def get_all(self, filter_obj: Optional[Dict[str, Any]] = None) -> List[ModelType]:
        if filter_obj is None:
            filter_obj = {}
        query = self._apply_filter(self.db.query(self.model), filter_obj)
        return query.all()

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

    def bulk_create(self, obj_ins:List[CreateSchemaType]) -> List[ModelType]:
        try:
            db_objs = [self.model(**obj_in.model_dump()) for obj_in in obj_ins]
            self.db.add_all(db_objs)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        return db_objs

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
    
    def _apply_filter(self, query, filter_obj: Dict[str, Any]):
        for key, value in filter_obj.items():
            if value == None:
                continue
            column = getattr(self.model, key, None)
            if column is None:
                continue
            col_type = self.model.__table__.c[key].type
            if isinstance(col_type, String):
                query = query.filter(column.like(f"%{value}%"))
            else:
                query = query.filter(column == value)
        return query
