from typing import List
from llama_index.core import (
    VectorStoreIndex,
    Document,
)
from backend.autodraft.utils import save_index, check_index_available
from backend.extensions import create_logger

logger = create_logger(__name__, level="DEBUG")


class IndexBuilder:

    def __init__(self, documents: List[Document], project_id: int):
        self.project_id = project_id
        self.documents = documents

        if check_index_available(project_id):
            raise FileExistsError(f"{self.project_id} Index already exists at . ")

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
