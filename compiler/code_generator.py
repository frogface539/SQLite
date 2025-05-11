from utils.logger import get_logger
from utils.errors import ExecutionError
from utils.errors import CodegenError
from compiler.parser import Parser

logger = get_logger(__name__)

class CreateTableCommand:
    def __init__(self, columns, table_name):
        logger.debug(f"Creating Table: {table_name} with columns: {columns}")
        self.columns = columns
        self.table_name = table_name
        logger.info(f"Table {table_name} creation with columns finished.")

class SelectTableCommand:
    def __init__(self, columns, table_name, where_clause=None):
        self.columns = columns
        self.table_name = table_name
        self.where_clause = where_clause

class UpdateTableCommand:
    def __init__(self, table_name, updates, where_clause=None):
        self.table_name = table_name
        self.updates = updates
        self.where_clause = where_clause

class InsertCommand:
    def __init__(self, table_name, values):
        self.table_name = table_name
        self.values = values

class DeleteCommand:
    def __init__(self, table_name, where_clause=None):
        self.table_name = table_name
        self.where_clause = where_clause

class DropCommand:
    def __init__(self, table_name):
        self.table_name = table_name


class CodeGeneration:
    def gen(self, parsed_statement):
        statement_type = parsed_statement["type"]

        if statement_type == "SELECT":
            return SelectTableCommand(
                table_name=parsed_statement["table_name"],
                columns=parsed_statement["columns"],
                where_clause=parsed_statement.get("where")
            )

        elif statement_type == "INSERT":
            return InsertCommand(
                table_name=parsed_statement["table_name"],
                values=parsed_statement["values"]
            )

        elif statement_type == "UPDATE":
            return UpdateTableCommand(
                table_name=parsed_statement["table_name"],
                updates=parsed_statement["updates"],
                where_clause=parsed_statement.get("where")
            )

        elif statement_type == "DELETE":
            return DeleteCommand(
                table_name=parsed_statement["table_name"],
                where_clause=parsed_statement.get("where")
            )

        elif statement_type == "DROP":
            return DropCommand(
                table_name=parsed_statement["table_name"]
            )

        elif statement_type == "CREATE":
            return CreateTableCommand(
                table_name=parsed_statement["table_name"],
                columns=parsed_statement["columns"]
            )

        else:
            logger.error(f"Unsupported statement type: {statement_type}")
            raise ExecutionError(f"Unsupported statement type: {statement_type}")



class PlanGenerator:
    def __init__(self, schema_registry=None):
        self.schema_registry = schema_registry or {}
        self.label_counter = 0
    
    def _new_label(self):
        """Generate unique labels for control flow"""
        self.label_counter += 1
        return f"label_{self.label_counter}"

    def generate_plan(self, command):
        """Generate low-level opcode sequence from command object"""
        logger.info(f"Generating execution plan for {type(command).__name__}")
        
        try:
            if isinstance(command, InsertCommand):
                return self._generate_insert_plan(command)
            elif isinstance(command, CreateTableCommand):
                return self._generate_create_table_plan(command)
            elif isinstance(command, DeleteCommand):
                return self._generate_delete_plan(command)
            elif isinstance(command, DropCommand):
                return self._generate_drop_table_plan(command)
            elif isinstance(command, SelectTableCommand):
                return self._generate_select_plan(command)
            elif isinstance(command, UpdateTableCommand):
                return self._generate_update_plan(command)
            else:
                raise ValueError(f"Unsupported command type: {type(command)}")
                
        except Exception as e:
            logger.error(f"Plan generation failed: {str(e)}")
            raise CodegenError(f"Plan generation error: {str(e)}") from e

    def _generate_insert_plan(self, cmd):
        """Generate opcodes for INSERT:
        [LOAD_CONST val1, LOAD_CONST val2, ..., INSERT table]"""
        logger.debug(f"Generating INSERT plan for {cmd.table_name}")
        
        plan = []
        for val in cmd.values:
            plan.append(("LOAD_CONST", val))
        plan.append(("INSERT_ROW", cmd.table_name))
        
        logger.debug(f"Generated INSERT plan: {plan}")
        return plan

    def _generate_select_plan(self, cmd):
        """Generate opcodes for SELECT:
        [OPEN_TABLE, SCAN_START, (FILTER), EMIT_ROW, SCAN_END]"""
        logger.debug(f"Generating SELECT plan for {cmd.table_name}")
        
        plan = [
            ("OPEN_TABLE", cmd.table_name),
            ("SCAN_START")
        ]
        
        # WHERE clause handling
        if cmd.where_clause:
            skip_label = self._new_label()
            plan.extend([
                ("LOAD_COLUMN", cmd.where_clause["column"]),
                ("LOAD_CONST", cmd.where_clause["value"]),
                ("COMPARE_EQ"),
                ("JUMP_IF_FALSE", skip_label)
            ])
        
        # Projection
        plan.append(("EMIT_ROW", cmd.columns))
        
        if cmd.where_clause:
            plan.append(("LABEL", skip_label))
        
        plan.append(("SCAN_END"))
        
        logger.debug(f"Generated SELECT plan: {plan}")
        return plan

    def _generate_update_plan(self, cmd):
        """Generate opcodes for UPDATE:
        [OPEN_TABLE, SCAN_START, (FILTER), UPDATE_ROW, SCAN_END]"""
        logger.debug(f"Generating UPDATE plan for {cmd.table_name}")
        
        # Validation
        if cmd.table_name not in self.schema_registry:
            raise CodegenError(f"Table '{cmd.table_name}' not found")
            
        plan = [
            ("OPEN_TABLE", cmd.table_name),
            ("SCAN_START")
        ]
        
        # WHERE clause
        if cmd.where_clause:
            skip_label = self._new_label()
            plan.extend([
                ("LOAD_COLUMN", cmd.where_clause["column"]),
                ("LOAD_CONST", cmd.where_clause["value"]),
                ("COMPARE_EQ"),
                ("JUMP_IF_FALSE", skip_label)
            ])
        
        # Updates
        for col, val in cmd.updates.items():
            plan.extend([
                ("LOAD_CONST", val),
                ("UPDATE_COLUMN", col)
            ])
        
        if cmd.where_clause:
            plan.append(("LABEL", skip_label))
        
        plan.append(("SCAN_END"))
        
        logger.debug(f"Generated UPDATE plan: {plan}")
        return plan

    def _generate_delete_plan(self, cmd):
        """Generate opcodes for DELETE:
        [OPEN_TABLE, SCAN_START, (FILTER), DELETE_ROW, SCAN_END]"""
        logger.debug(f"Generating DELETE plan for {cmd.table_name}")
        
        plan = [
            ("OPEN_TABLE", cmd.table_name),
            ("SCAN_START")
        ]
        
        if cmd.where_clause:
            skip_label = self._new_label()
            plan.extend([
                ("LOAD_COLUMN", cmd.where_clause["column"]),
                ("LOAD_CONST", cmd.where_clause["value"]),
                ("COMPARE_EQ"),
                ("JUMP_IF_FALSE", skip_label),
                ("DELETE_ROW",),
                ("LABEL", skip_label)
            ])
        else:
            plan.append(("DELETE_ROW",))
            
        plan.append(("SCAN_END"))
        
        logger.debug(f"Generated DELETE plan: {plan}")
        return plan

    def _generate_create_table_plan(self, cmd):
        """Generate opcodes for CREATE TABLE"""
        logger.debug(f"Generating CREATE TABLE plan for {cmd.table_name}")
        plan = [("CREATE_TABLE", cmd.table_name, cmd.columns)]
        logger.debug(f"Generated CREATE plan: {plan}")
        return plan

    def _generate_drop_table_plan(self, cmd):
        """Generate opcodes for DROP TABLE"""
        logger.debug(f"Generating DROP TABLE plan for {cmd.table_name}")
        plan = [("DROP_TABLE", cmd.table_name)]
        logger.debug(f"Generated DROP plan: {plan}")
        return plan