import hashlib

from fastapi import UploadFile


class Md5Utils:

    @staticmethod
    async def calculate_md5(file: UploadFile) -> str:
        md5 = hashlib.md5()
        while chunk := await file.read(8192):
            md5.update(chunk)
        await file.seek(0)
        return md5.hexdigest()
