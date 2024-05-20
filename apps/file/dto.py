from core.base_dto import BaseResponse


class FileResponse(BaseResponse):
    original_filename: str
    saved_filename: str
