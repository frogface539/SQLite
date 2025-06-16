from backend.os_interface import OSInterface
from collections import OrderedDict

class Page:
    def __init__(self, number: int, data: bytes, dirty=False):
        self.number = number
        self.data = data
        self.dirty = dirty
        

class Pager:
    def __init__(self, os_interface: OSInterface, cache_size = 64):
        self.os_interface = os_interface  
        self.cache_size = cache_size
        self.cache = OrderedDict()   # page_number -> Page
        self.dirty_pages = set()
        self.page_size = os_interface.page_size

    #  returns a page from cache or loads from disk
    def get_page(self, page_number: int) -> Page:
        if page_number in self.cache:
            self.cache.move_to_end(page_number) # LRU Cache
            return self.cache[page_number]
        
        data = self.os_interface.read_page(page_number)
        page = Page(page_number, data)
        self._cache_page(page)
        return page
    
    # flags a page and bumps it in LRU
    def mark_dirty(self, page: Page):
        page.dirty = True
        self._cache_page(page)  # refresh LRU

    # writing dirty pages to disk
    def flush_all(self):
        for page in list(self.cache.values()):
            self._flush_page(page)
        self.cache.clear()

    def _flush_page(self, page: Page):
        if page.dirty:
            self.os_interface.write_page(page.number, page.data)
            page.dirty = False

    def _cache_page(self, page: Page):
        if len(self.cache) >= self.cache_size:
            old_page = next(iter(self.cache.values()))
            self._flush_page(old_page)
            self.cache.pop(old_page.number)
        self.cache[page.number] = page

    @property
    def num_pages(self):
        return (self.os_interface.file_size + self.page_size - 1) // self.page_size