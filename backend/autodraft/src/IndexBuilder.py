from abc import ABC, abstractmethod
import os
import shutil
from typing import List, Optional
from llama_index.core import (
    StorageContext,
    load_index_from_storage,
    VectorStoreIndex,
    SimpleDirectoryReader,
    Document,
)
import json
from backend.autodraft.utils import save_index, S3_INDEX_DIR
from backend.src.s3 import S3
from backend.config import Config
from backend.extensions import create_logger

logger = create_logger(__name__, level="DEBUG")


class IndexBuilder:

    def __init__(self, documents: List[Document], project_id: int):
        self.project_id = project_id
        self.documents = documents

        # first, check if the index exists
        s3 = S3(bucket=Config.AUTODRAFT_BUCKET)
        if s3.exists(f"{S3_INDEX_DIR}/{self.project_id}"):
            raise FileExistsError(
                f"Index already exists at {S3_INDEX_DIR}/{self.project_id}. "
            )

    def build_index(self):

        # TODO: just using defaults here
        index = VectorStoreIndex.from_documents(
            documents=self.documents,
        )

        save_index(index, self.project_id)

        return index

    def update_index(self, save_to_disk=False) -> bool:
        # TODO: implement
        raise NotImplementedError
