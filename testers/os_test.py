from backend.os_interface import OSInterface, DEFAULT_PAGE_SIZE

def test_os_interface():
    db = OSInterface("example.db")
    try:
        db.open_file()

        # Write to Page 0 (4096 bytes)
        message = b'HelloWorld'
        padding = DEFAULT_PAGE_SIZE - len(message)
        data = message + b'\x00' * padding
        db.write_page(0, data)

        # Read to Page 0
        read_data = db.read_page(0)
        print("First 20 bytes of page 0: ", read_data[:20])

    finally:
        db.close_file()

if __name__ == "__main__":
    test_os_interface()