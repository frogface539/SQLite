from utils.logger import get_logger
from utils.errors import ExecutionError
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
    def generate_plan(self, command):
        logger.debug(f"Generating execution plan for: {type(command).__name__}")

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
            logger.error(f"Unsupported command type: {type(command)}")
            raise ValueError(f"Unsupported command type: {type(command)}")

    def _generate_insert_plan(self, cmd):
        logger.debug(f"Generating plan for INSERT command on table {cmd.table_name}")
        plan = []
        for val in cmd.values:
            plan.append(("LOAD_CONST", val))
        plan.append(("INSERT", cmd.table_name))
        return plan

    def _generate_create_table_plan(self, cmd):
        logger.debug(f"Generating plan for CREATE TABLE command on table {cmd.table_name}")
        return [("CREATE_TABLE", cmd.table_name, cmd.columns)]

    def _generate_delete_plan(self, cmd):
        logger.debug(f"Generating plan for DELETE command on table {cmd.table_name}")
        return [("DELETE", cmd.table_name, cmd.where_clause or "No WHERE clause")]

    def _generate_drop_table_plan(self, cmd):
        logger.debug(f"Generating plan for DROP TABLE command on table {cmd.table_name}")
        return [("DROP_TABLE", cmd.table_name)]

    def _generate_select_plan(self, cmd):
        logger.debug(f"Generating plan for SELECT command on table {cmd.table_name}")
        # Handling case for SELECT * (all columns)
        if "*" in cmd.columns:
            cmd.columns = ["*"]
        return [("SELECT", cmd.table_name, cmd.columns, cmd.where_clause or "No WHERE clause")]

    def _generate_update_plan(self, cmd):
        logger.debug(f"Generating plan for UPDATE command on table {cmd.table_name}")
        return [("UPDATE", cmd.table_name, cmd.updates, cmd.where_clause or "No WHERE clause")]
