from backend.src.s3 import S3, create_s3_fs
from backend.autodraft.utils import check_index_available

print(check_index_available(1, create_s3_fs()))
