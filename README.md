﻿# 🧠 SQLite-Like Database Engine in Python

A low-level prototype of a SQLite-style database engine implemented from scratch in Python. This project emulates core storage engine features such as disk paging, memory management, and B-tree indexing — all without any external database libraries.

---

## 📦 Features

### ✅ Core Components:
- **Pager System**  
  - Page-level read/write abstraction over a raw binary file  
  - Page caching with dirty marking and flush support  
  - Fixed-size page format (`DEFAULT_PAGE_SIZE = 4096`)

- **B-Tree Index**  
  - Supports recursive key insertion and internal node splitting  
  - Handles promotion, overflow, and multi-level tree structure  
  - Custom binary serialization/deserialization per node  
  - Duplicate key detection with warning logs  
  - Configurable branching factor (`MAX_KEYS = 3`)

- **Virtual Filesystem Layer**
  - Implemented as `OSInterface`, wrapping binary file I/O  
  - Handles file open, seek, read, write, and length management  

- **Logging & Debugging**
  - Integrated with Python `logging` for detailed inspection  
  - Rich UI tables and trees for paging and B-tree visualization  
  - Explicit error types via custom `BTreeError` exception  

- **SQL Script Execution (Early Stage)**
  - Accepts `.sql` files and compiles rudimentary DDL into planner ops  
  - Basic table creation parsing (e.g. `CREATE TABLE`)  

---

## 📁 Project Structure

```
SQLite Project/
├── backend/
│   ├── b_tree.py             # B-tree logic (node split, insert, search)
│   ├── pager.py              # Page cache & allocation
│   ├── os_interface.py       # File I/O abstraction
│   ├── database_engine.py    # Orchestrates pager, tree, and interface
│
├── utils/
│   ├── errors.py             # Custom exceptions (e.g., BTreeError)
│   ├── logger.py             # Configured logger for debug output
│
├── ui/
│   ├── rich_inspector.py     # Table/tree printouts of pager and B-tree
│
├── test.sql                  # Test SQL script
├── example.db                # Auto-generated binary database file
├── main.py                   # Entry point for script execution
```
| Layer      | Tools Used                            |
| ---------- | ------------------------------------- |
| Language   | Python 3.12                           |
| Logging    | `logging` module                      |
| UI Display | `rich` (for tables, trees)            |
| Testing    | Manual `test.sql` + custom inspection |
| File I/O   | Binary `rb+/wb+` modes                |

🚀 Running the Project
```bash
Copy
Edit
python main.py test.sql
View debug logs in terminal

Inspect serialized B-tree state

Test .sql table creation or inserts
```
📬 Contact
Author: Lakshay Jain
LinkedIn: https://www.linkedin.com/in/lakshay-jain-a48979289/
GitHub: https://github.com/frogface539/
