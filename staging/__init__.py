from .staged_file import StagedFile
from .staging_area import StagingArea


class StagingException(Exception):
    def __init__(self, status: int, title: str, detail: str=None, *args) -> None:
        super().__init__(*args)
        self.status = status
        self.title = title
        self.detail = detail
