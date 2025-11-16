from enum import Enum
from typing import List


class FileType(str, Enum):
    # Папки
    FOLDER = "folder"
    FOLDER_FILLED = "folder-filled"
    
    # Документация
    README = "readme"
    
    # Диаграммы и схемы
    ARCHITECTURE = "architecture"
    DATABASE = "database"
    
    # Ссылки
    DEMO = "demo"
    GITHUB = "github"
    
    # API документация
    SWAGGER = "swagger"


ALL_FILE_TYPES: List[str] = [ft.value for ft in FileType]

VALID_FILE_TYPES: List[str] = ALL_FILE_TYPES

