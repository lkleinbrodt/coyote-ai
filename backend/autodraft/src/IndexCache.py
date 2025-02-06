from collections import OrderedDict
from datetime import datetime, timedelta
from llama_index.core import VectorStoreIndex
from backend.extensions import create_logger
from backend.autodraft.utils import load_index

logger = create_logger(__name__)


class IndexCache:
    # TODO: take the expiration component from below and add it here
    # after X minutes, delete unused indices
    def __init__(self):
        self.cache = {}

    def get_index(self, project_id):
        if project_id in self.cache:
            return self.cache[project_id]

        logger.warning(f"Index not loaded for project {project_id}, loading it now")
        # raises FileNotFoundError if not found
        self.cache[project_id] = load_index(project_id)
        return self.cache[project_id]


class OldIndexCache:
    """
    A cache implementation for storing index data. Basically a dict with the following 2 features:
    - A maximum size, after which the oldest items are removed.
        - size is calculated as the number of nodes in the index
        - this isnt perfect, but it's a way of estimating
    - A time-to-live (TTL) for each item, after which the item is removed.

    Args:
        max_size (int): The maximum number of items that can be stored in the cache.
        max_node_size (int): Maximum number of nodes (across all indexes).
        ttl (int): The time-to-live (in seconds) for each item in the cache.

    Attributes:
        max_size (int): The maximum number of items that can be stored in the cache.
        max_node_size (int): Maximum number of nodes (across all indexes).
        ttl (int): The time-to-live (in seconds) for each item in the cache.

    """

    def __init__(self, max_size, max_node_size, ttl):
        self.max_size = max_size
        self.max_node_size = max_node_size
        self.ttl = ttl
        self._data = OrderedDict()

    def __getitem__(self, key):
        value, expiration_time, node_size = self._data[key]
        if expiration_time < datetime.utcnow():
            del self._data[key]
            raise KeyError(key)
        return value

    def count_nodes(self, index: VectorStoreIndex):
        """this probably belongs as a method for an index class, but we havent built one yet so it's here
        Remember that total size = nodes * chunk size (plus the overhead)
        """
        if index is None:
            return 0
        docstore = index.docstore

        return len(docstore.docs)

    def __setitem__(self, key, value, ttl=None):
        expiration_time = (
            datetime.utcnow() + timedelta(seconds=ttl)
            if ttl
            else datetime.utcnow() + timedelta(seconds=self.ttl)
        )

        node_size = self.count_nodes(value)

        while (
            self.max_node_size is not None
            and self._get_current_node_size() + node_size > self.max_node_size
        ):
            self._data.popitem(last=False)

        self._data[key] = (value, expiration_time, node_size)

    def __delitem__(self, key):
        del self._data[key]

    def __contains__(self, key):
        try:
            value, expiration_time, _ = self._data[key]
            return expiration_time >= datetime.utcnow()
        except KeyError:
            return False

    def __len__(self):
        self._remove_expired_entries()
        return len(self._data)

    def _get_current_node_size(self):
        return sum(entry[2] for entry in self._data.values())

    def _remove_expired_entries(self):
        current_time = datetime.utcnow()
        self._data = {
            key: (value, expiration_time, node_size)
            for key, (value, expiration_time, node_size) in self._data.items()
            if expiration_time >= current_time
        }

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default
