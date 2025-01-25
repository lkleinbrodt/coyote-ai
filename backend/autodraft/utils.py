from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core import load_index_from_storage
import os
from backend.autodraft.models import File
from llama_index.core import Document as LlamaDocument
from backend.src.s3 import S3, create_s3_fs
from backend.config import Config


# TODO: implement s3 save/loading, make sure to adjust index builder etc (which should be using these set functions, not rolling it's own save to storage (perhaps use an index IO class or something?)

S3_INDEX_DIR = Config.AUTODRAFT_BUCKET + "/" + Config.S3_INDEX_DIR


def save_index(index: VectorStoreIndex, project_id: int):
    s3_fs = create_s3_fs()
    # TODO: more config
    index.storage_context.persist(
        persist_dir=f"{S3_INDEX_DIR}/{project_id}",
        fs=s3_fs,
    )

    return True


def load_index(project_id: int) -> VectorStoreIndex | None:
    s3_fs = create_s3_fs()
    # if no dir exists at the given path, then raise an error
    if not s3_fs.exists(f"{S3_INDEX_DIR}/{project_id}"):
        raise FileNotFoundError(
            f"Index not found at {S3_INDEX_DIR}/{project_id}. Please create an index first."
        )
    index = load_index_from_storage(
        StorageContext.from_defaults(
            persist_dir=f"{S3_INDEX_DIR}/{project_id}", fs=s3_fs
        )
    )
    return index


def update_index(project_id):
    index = load_index(project_id)

    if not index:
        return None

    files = File.query.filter_by(project_id=project_id).all()
    documents = []
    for file in files:
        documents.extend(file.documents)

    llama_documents = [
        LlamaDocument(
            text=doc.content,
            metadata=doc.llama_metadata,
            doc_id=doc.llama_id,
            id_=doc.id,
        )
        for doc in documents
    ]

    # TODO: delete docs that are no longer necessary
    index.refresh_ref_docs(llama_documents)

    # Save the updated index to S3
    save_index(index, project_id)

    return index


def delete_index(project_id) -> bool:
    index_path = S3_INDEX_DIR / str(project_id)
    s3_fs = create_s3_fs()
    if s3_fs.exists(index_path):
        try:
            s3_fs.rm(index_path, recursive=True)
            return True
        except Exception as e:
            return False
    else:
        return False


def check_index_available(project_id, s3_fs=None) -> bool:
    index_path = S3_INDEX_DIR + "/" + str(project_id)
    if not s3_fs:
        s3_fs = create_s3_fs()
    return s3_fs.exists(index_path)
