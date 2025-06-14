from backend.os_interface import OSInterface, DEFAULT_PAGE_SIZE
from backend.pager import Pager

def test_pager():
    osi = OSInterface("example.db")
    osi.open_file()
    pager = Pager(osi, cache_size=2)

    try:
        # Read page 0 (may be empty if db is new)
        page0 = pager.get_page(0)
        print("Before write - Page 0:", page0.data[:20])

        # Modify page 0
        page0.data = b"PageZero" + b"\x00" * (DEFAULT_PAGE_SIZE - 8)
        pager.mark_dirty(page0)

        # Modify page 1
        page1 = pager.get_page(1)
        page1.data = b"PageOne" + b"\x00" * (DEFAULT_PAGE_SIZE - 7)
        pager.mark_dirty(page1)

        # Modify page 2
        page2 = pager.get_page(2)
        page2.data = b"PageTwo" + b"\x00" * (DEFAULT_PAGE_SIZE - 7)
        pager.mark_dirty(page2)

        # Flush all dirty pages to disk
        pager.flush_all()
        print("Pages written to disk.")

        # Read back to verify persistence
        page0_reloaded = pager.get_page(0)
        print("After write - Page 0:", page0_reloaded.data[:20])

        page1_reloaded = pager.get_page(1)
        print("After write - Page 1:", page1_reloaded.data[:20])

        page2_reloaded = pager.get_page(2)
        print("After write - Page 2:", page2_reloaded.data[:20])

    finally:
        osi.close_file()

if __name__ == "__main__":
    test_pager()
