import os
from utils.logger import get_logger
from utils.errors import ExecutionError
logger = get_logger(__name__)

DEFAULT_PAGE_SIZE = 4096

class OSInterface:
    def __init__(self, filepath, page_size = DEFAULT_PAGE_SIZE):
        self.filepath = filepath
        self.page_size = page_size
        self.fd = None
        logger.debug(f"Initialized OS-Interface with file: {self.filepath}, page size: {self.page_size}")

    def open_file(self):
        try:
            if not os.path.exists(self.filepath):
                with open(self.filepath, 'wb') as f:
                    f.write(b'\x00' * self.page_size)
                    logger.info(f"Created new file '{self.filepath}' with one empty page")

            self.fd = open(self.filepath, 'r+b')
            logger.info(f"Opened file '{self.filepath}' successfully")

        except Exception as e:
            logger.error(f"Error opening file: {e}")
            raise ExecutionError("Error opening file")
    
    def close_file(self):
        if self.fd:
            try:
                self.fd.close()
                logger.info(f"Closed file '{self.filepath}'")

            except Exception as e:
                logger.error(f"Error closing file: {e}")
                raise ExecutionError("Error closing the file")
            
            finally:
                self.fd = None

    def read_page(self, page_number):
        if self.fd is None:
            raise RuntimeError("File not open. Use open_file() first.")

        try:
            offset = page_number * self.page_size
            self.fd.seek(offset)
            data = self.fd.read(self.page_size)
            logger.debug(f"Read page {page_number} (offset {offset})")
            return data
        
        except Exception as e:
            logger.error(f"Error reading page {page_number}: {e}")
            raise ExecutionError("Error reading page ")

    def write_page(self, page_number, data):
        if self.fd is None:
            raise RuntimeError("File not open. Use open_file() first.")
        
        if len(data) != self.page_size:
            raise ValueError(f"Data must be exactly {self.page_size} bytes")

        try:
            offset = page_number * self.page_size
            self.fd.seek(offset)
            self.fd.write(data)
            self.fd.flush()
            logger.debug(f"Wrote page {page_number} (offset {offset})")

        except Exception as e:
            logger.error(f"Error writing page {page_number}: {e}")
            raise ExecutionError("Error writing page")
    
