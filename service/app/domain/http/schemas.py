from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class HTTPResponse(BaseModel, Generic[T]):
    code: int = Field(default=200, description="业务状态码")
    message: str = Field(default="success", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    success: bool = Field(default=True, description="请求是否成功")

    @classmethod
    def ok(
        cls,
        data: Optional[T] = None,
        message: str = "success",
        code: int = 200,
    ) -> "HTTPResponse[T]":
        return cls(code=code, message=message, data=data, success=True)

    @classmethod
    def fail(
        cls,
        message: str = "fail",
        code: int = 500,
        data: Optional[T] = None,
    ) -> "HTTPResponse[T]":
        return cls(code=code, message=message, data=data, success=False)

class HTTPResponsePage(BaseModel, Generic[T]):
    code: int = Field(default=200, description="业务状态码")
    message: str = Field(default="success", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    success: bool = Field(default=True, description="请求是否成功")
    total: int = Field(default=0, description="总条数")
    current: int = Field(default=0, description="当前页")
    size: int = Field(default=0, description="每页条数")

    @classmethod
    def ok(
        cls,
        data: Optional[T] = None,
        message: str = "success",
        code: int = 200,
        total: int = 0,
        current: int = 0,
        size: int = 0,
    ) -> "HTTPResponsePage[T]":
        return cls(code=code, message=message, data=data, success=True, total=total, current=current, size=size)

    @classmethod
    def fail(
        cls,
        message: str = "fail",
        code: int = 500,
        data: Optional[T] = None,
        total: int = 0,
        current: int = 0,
        size: int = 0,
    ) -> "HTTPResponsePage[T]":
        return cls(code=code, message=message, data=data, success=False, total=total, current=current, size=size)
