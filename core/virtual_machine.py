from utils.errors import ExecutionError
from utils.logger import get_logger

logger = get_logger(__name__)

class VirtualMachine:
    def __init__(self , schema_registry=None):
        self.tables = {}                         # For storing in-memory tables
        self.schema = schema_registry or {}
        self.stack = []
        self.cursor = None
        self.current_table = None
        self.current_row = None                  # Ensure current_row is initialized
        self.labels = {}
        self.program_counter = 0
    
    def execute(self, plan):
        """Execute a plan"""
        self.program_counter = 0
        plan_length = len(plan)

        results = []

        self.labels = {
            op[1]: idx for idx, op in enumerate(plan)
            if isinstance(op, tuple) and len(op) > 1 and op[0] == 'LABEL'
        }

        while self.program_counter < plan_length:
            opcode = plan[self.program_counter]

            # wrap strings into tuples
            if isinstance(opcode, str):
                opcode = (opcode,)

            op = opcode[0]
            arguments = opcode[1:]

            try:
                if op == "OPEN_TABLE":
                    self._open_table(arguments[0])

                elif op == "CREATE_TABLE":
                    self._create_table(arguments[0], arguments[1])

                elif op == "DROP_TABLE":       
                    self._drop_table(arguments[0])

                elif op == "INSERT_ROW":
                    self._insert_row(arguments[0])

                elif op == "SCAN_START":
                    self._scan_start()

                elif op == "SCAN_NEXT":
                    if not self._scan_next():
                        break

                elif op == "SCAN_END":
                    self._scan_end()

                elif op == "LOAD_CONST":
                    self.stack.append(arguments[0])

                elif op == "LOAD_COLUMN":
                    self._load_column(arguments[0])

                elif op == "COMPARE_EQ":
                    self._compare("==")

                elif op == "COMPARE_NEQ":
                    self._compare("!=")
                
                elif op == "COMPARE_LT":
                    self._compare("<")
                
                elif op == "COMPARE_LTE":
                    self._compare("<=")

                elif op == "COMPARE_GT":
                    self._compare(">")

                elif op == "COMPARE_GTE":
                    self._compare(">=")

                elif op == "JUMP_IF_FALSE":
                    self._jump_if_false(arguments[0])

                elif op == "JUMP":
                    self.program_counter = self.labels[arguments[0]] - 1 

                elif op == "LABEL":
                    pass

                elif op == "EMIT_ROW":
                    row = self._emit_row(arguments[0]) if arguments else self._emit_row()
                    results.append(row)

                elif op == "UPDATE_COLUMN":
                    self._update_column(arguments[0])

                elif op == "DELETE_ROW":
                    self._delete_row()

                else:
                    raise ExecutionError(f"Unknown opcode: {op}")
                
                self.program_counter += 1

            except Exception as e:
                raise ExecutionError(f"Error executiong {op}: {str(e)}")
            
        return results

    # Implementing the OpCodes
    def _open_table(self, table_name):
        if table_name not in self.tables:
            raise ExecutionError(f"Table '{table_name}' not found")
        
        self.current_table = self.tables[table_name]

    def _create_table(self, table_name, columns):
        if table_name in self.tables:
            raise ExecutionError(f"Table: '{table_name}' already exists")
        
        self.tables[table_name] = []
        self.schema[table_name] = columns
        logger.info(f"Created table '{table_name}' with columns: {columns}")

    def _drop_table(self, table_name):
        if table_name not in self.tables:
            raise ExecutionError("Table '{table_name}' does not exist")
        
        del self.tables[table_name]
        del self.schema[table_name]
        logger.info(f"Dropped table '{table_name}'")

    def _insert_row(self, table_name):
        if table_name not in self.tables:
            raise ExecutionError(f"Table {table_name} does not exists")
        
        column_defs = self.schema[table_name]
        columns = [col if isinstance(col, str) else col['name'] for col in column_defs]

        if len(self.stack) < len(columns):
            raise ExecutionError("Not Enough values for Insertion")
        
        row = {}
        for col in reversed(columns):
            row[col] = self.stack.pop()

        self.tables[table_name].append(row)
        logger.debug(f"Inserted row into '{table_name}': {row}")

    def _scan_start(self):
        if not self.current_table:
            raise ExecutionError("No table opened for scanning")
            
        self.cursor = iter(self.current_table)
        self.current_row = None

    def _scan_next(self):
        try:
            self.current_row = next(self.cursor)
            self.stack.append(True)     
            return True
        except StopIteration:
            self.current_row = None
            self.stack.append(False)    
            return False
    
    def _scan_end(self):
        self.cursor = None
        self.current_row = None

    def _load_column(self, column_name):
        if not self.current_row:
            raise ExecutionError("No active row for column access")
        
        if column_name not in self.current_row:
            raise ExecutionError(f"Column '{column_name}' not found")
        
        self.stack.append(self.current_row[column_name])

    def _compare(self, operator):
        if len(self.stack) < 2:
            raise ExecutionError("Not enough values for comparison")
        right = self.stack.pop()
        left = self.stack.pop()

        if operator == "==":
            self.stack.append(left == right)

        elif operator == "!=":
            self.stack.append(left != right)

        elif operator == "<":
            self.stack.append(left < right)

        elif operator == "<=":
            self.stack.append(left <= right)

        elif operator == ">":
            self.stack.append(left > right)

        elif operator == ">=":
            self.stack.append(left >= right)

        else:
            raise ExecutionError(f"Unsupported operator: {operator}")
    
    def _jump_if_false(self, label):
        if len(self.stack) == 0:
            raise ExecutionError("No condition to jump on")
        
        if not self.stack.pop():
            if label not in self.labels:
                raise ExecutionError(f"Undefined label: {label}")
            
            self.program_counter = self.labels[label] - 1

    def _emit_row(self, columns=None):
        if not self.current_row:
            raise ExecutionError("No row to emit")
        
        if columns and columns == ["*"]:
            return self.current_row.copy()
        
        return {col: self.current_row[col] for col in columns} if columns else self.current_row.copy()

    def _update_column(self, column_name):
        if not self.current_row:
            raise ExecutionError("No active row to update")
        
        if column_name not in self.current_row:
            raise ExecutionError(f"Column '{column_name}' not found")
        
        if len(self.stack) == 0:
            raise ExecutionError("No value to update with")
        
        self.current_row[column_name] = self.stack.pop()

    def _delete_row(self):
        if not self.current_row or not self.current_table:
            raise ExecutionError("No active row to delete")
        
        self.current_table.remove(self.current_row)
        logger.debug(f"Deleted row: {self.current_row}")
        