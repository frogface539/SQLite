import struct
from utils.logger import get_logger
from utils.errors import BTreeError
from backend.os_interface import DEFAULT_PAGE_SIZE

logger = get_logger(__name__)

class BTreeNode:
    def __init__(self, keys=None, children=None, is_leaf=True):
        self.keys = keys or []
        self.children = children or []
        self.is_leaf = is_leaf

    def serialize(self):
        try:
            header = struct.pack("<?I", self.is_leaf, len(self.keys))
            keys_data = b"".join(struct.pack("<I", key) for key in self.keys)
            data = header + keys_data
            if len(data) > DEFAULT_PAGE_SIZE:
                raise BTreeError("Serialized node exceeds page size")
            data += b'\x00' * (DEFAULT_PAGE_SIZE - len(data))  # pad to full page
            return data
        except Exception as e:
            raise BTreeError(f"Serialization failed: {e}")

    @staticmethod
    def deserialize(data):
        try:
            if len(data) < 5:
                raise BTreeError("Page too small to deserialize")
            is_leaf = bool(data[0])
            key_count = struct.unpack("<I", data[1:5])[0]
            if key_count > 1024:
                raise BTreeError(f"Unrealistic key count: {key_count}")
            keys = list(struct.unpack(f"<{key_count}I", data[5:5 + key_count * 4]))
            return BTreeNode(keys=keys, is_leaf=is_leaf)
        except Exception as e:
            raise BTreeError(f"Failed to deserialize B-tree node: {e}")

class BTree:
    def __init__(self, pager):
        self.pager = pager
        self.page_size = pager.page_size
        self.root_page_num = 0
        try:
            self.root = self._load_node(self.root_page_num)
        except BTreeError:
            self.root = BTreeNode(is_leaf=True)
            self._write_node(self.root_page_num, self.root)

    def _load_node(self, page_num):
        try:
            page = self.pager.get_page(page_num)
            node = BTreeNode.deserialize(page.data)
            logger.debug(f"Loaded node from page {page_num}: {node.keys}")
            return node
        except Exception as e:
            raise BTreeError(f"Error loading node from page {page_num}: {e}")

    def _write_node(self, page_num, node):
        try:
            page = self.pager.get_page(page_num)
            serialized = node.serialize()
            page.data = serialized
            self.pager.mark_dirty(page)
            logger.debug(f"Wrote node to page {page_num} with keys: {node.keys}")
        except Exception as e:
            raise BTreeError(f"Error writing node to page {page_num}: {e}")

    def insert(self, key):
        if key in self.root.keys:
            logger.warning(f"Key {key} already exists in root.")
            return
        self.root.keys.append(key)
        self.root.keys.sort()
        self._write_node(self.root_page_num, self.root)
        logger.info(f"Inserted key {key} into root node.")

    def search(self, key):
        return key in self.root.keys
