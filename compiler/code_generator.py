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
        loop_label = self._new_label()
        end_label = self._new_label()

        plan = [
            ("OPEN_TABLE", cmd.table_name),
            ("SCAN_START",),
            ("LABEL", loop_label),
            ("SCAN_NEXT",),
            ("JUMP_IF_FALSE", end_label),
        ]

        # Optional WHERE clause
        if cmd.where_clause:
            skip_label = self._new_label()
            plan.extend([
                ("LOAD_COLUMN", cmd.where_clause["column"]),
                ("LOAD_CONST", str(cmd.where_clause["value"])),
                ("COMPARE_EQ",),
                ("JUMP_IF_FALSE", skip_label),
                ("EMIT_ROW", cmd.columns),
                ("LABEL", skip_label),
            ])
        else:
            plan.append(("EMIT_ROW", cmd.columns))

        plan.append(("JUMP", loop_label))
        plan.append(("LABEL", end_label))
        plan.append(("SCAN_END",))

        return plan


    def _generate_update_plan(self, cmd):
        plan = []

        loop_label = self._new_label()
        end_label = self._new_label()
        skip_label = self._new_label()

        plan.append(("OPEN_TABLE", cmd.table_name))
        plan.append(("SCAN_START",))
        plan.append(("LABEL", loop_label))
        plan.append(("SCAN_NEXT",))
        plan.append(("JUMP_IF_FALSE", end_label))

        # WHERE condition
        if cmd.where_clause:
            plan.extend([
                ("LOAD_COLUMN", cmd.where_clause["column"]),
                ("LOAD_CONST", str(cmd.where_clause["value"])),
                ("COMPARE_EQ",),
                ("JUMP_IF_FALSE", skip_label)
            ])

        # Perform update
        for column, value in cmd.updates.items():
            plan.extend([
                ("LOAD_CONST", str(value)),
                ("UPDATE_COLUMN", column)
            ])

        plan.append(("LABEL", skip_label))
        plan.append(("JUMP", loop_label))
        plan.append(("LABEL", end_label))
        plan.append(("SCAN_END",))

        return plan


    def _generate_delete_plan(self, cmd):
        plan = []

        loop_label = self._new_label()
        end_label = self._new_label()
        skip_label = self._new_label()

        plan.append(("OPEN_TABLE", cmd.table_name))
        plan.append(("SCAN_START",))
        plan.append(("LABEL", loop_label))
        plan.append(("SCAN_NEXT",))
        plan.append(("JUMP_IF_FALSE", end_label))

        # WHERE condition
        if cmd.where_clause:
            plan.extend([
                ("LOAD_COLUMN", cmd.where_clause["column"]),
                ("LOAD_CONST", str(cmd.where_clause["value"])),
                ("COMPARE_EQ",),
                ("JUMP_IF_FALSE", skip_label)
            ])

        # Delete if condition is met
        plan.append(("DELETE_ROW",))

        plan.append(("LABEL", skip_label))
        plan.append(("JUMP", loop_label))
        plan.append(("LABEL", end_label))
        plan.append(("SCAN_END",))

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