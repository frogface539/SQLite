import os
from utils.logger import get_logger
from utils.errors import ExecutionError
logger = get_logger(__name__)

DEFAULT_PAGE_SIZE = 4096

class OSInterface:
    def __init__(self, filepath, page_size = DEFAULT_PAGE_SIZE):
        self.filepath = filepath
        self.page_size = page_size
        self.file = None
        logger.debug(f"Initialized OS-Interface with file: {self.filepath}, page size: {self.page_size}")
        self.file = None

    def open_file(self):
        if self.file is None:
            self.file = open(self.filepath, "r+b") if os.path.exists(self.filepath) else open(self.filepath, "w+b")
        try:
            if not os.path.exists(self.filepath):
                with open(self.filepath, 'wb') as file:
                    file.write(b'\x00' * self.page_size)
                    logger.info(f"Created new file '{self.filepath}' with one empty page")

            self.file = open(self.filepath, 'r+b') 
            logger.info(f"Opened file '{self.filepath}' successfully")

        except Exception as e:
            logger.error(f"Error opening file: {e}")
            raise ExecutionError("Error opening file")
    
    def close_file(self):
        if self.file:
            try:
                self.file.close()
                logger.info(f"Closed file '{self.filepath}'")

            except Exception as e:
                logger.error(f"Error closing file: {e}")
                raise ExecutionError("Error closing the file")
            
            finally:
                self.file = None

    def read_page(self, page_number):
        if self.file is None:
            raise RuntimeError("File not open. Use open_file() first.")
        if self.file is None:
            raise RuntimeError("File not open. Use open_file() first.")

        try:
            offset = page_number * self.page_size
            self.file.seek(offset)
            data = self.file.read(self.page_size)
            logger.debug(f"Read page {page_number} (offset {offset})")
            return data
        
        except Exception as e:
            logger.error(f"Error reading page {page_number}: {e}")
            raise ExecutionError("Error reading page ")

    def write_page(self, page_number, data):
        if self.file is None:
            raise RuntimeError("File not open. Use open_file() first.")
        
        if len(data) != self.page_size:
            raise ValueError(f"Data must be exactly {self.page_size} bytes")

        try:
            offset = page_number * self.page_size
            self.file.seek(offset)
            self.file.write(data)
            self.file.flush()
            logger.debug(f"Wrote page {page_number} (offset {offset})")

        except Exception as e:
            logger.error(f"Error writing page {page_number}: {e}")
            raise ExecutionError("Error writing page")
    
    @property
    def file_size(self):
        if self.file is None:
            raise RuntimeError("File not opened before accessing file_size")
        current = self.file.tell()
        self.file.seek(0, os.SEEK_END)
        size = self.file.tell()
        self.file.seek(current, os.SEEK_SET)
        return size