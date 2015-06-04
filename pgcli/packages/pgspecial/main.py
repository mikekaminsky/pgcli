from . import export
from .iocommands import *
from .dbcommands import *

def show_help(*args):  # All the parameters are ignored.
    headers = ['Command', 'Description']
    result = []

    for command, value in sorted(COMMANDS.items()):
        if value[1]:
            result.append(value[1])
    return [(None, result, headers, None)]

def dummy_command(*args):
    """
    Used by commands that are actually handled elsewhere.
    But we want to keep their docstrings in the same list
    as all the rest of commands.
    """
    raise NotImplementedError

def in_progress(*args):
    """
    Stub method to signal about commands being under development.
    """
    raise NotImplementedError

COMMANDS = {
            '\?': (show_help, ['\?', 'Help on pgcli commands.']),
            '\c': (change_db, ['\c database_name', 'Connect to a new database.']),
            '\l': ('''SELECT datname FROM pg_database;''', ['\l', 'List databases.']),
            '\d': (describe_table_details, ['\d [pattern]', 'List or describe tables, views and sequences.']),
            '\dn': (list_schemas, ['\dn[+] [pattern]', 'List schemas.']),
            '\du': (list_roles, ['\du[+] [pattern]', 'List roles.']),
            '\\x': (toggle_expanded_output, ['\\x', 'Toggle expanded output.']),
            '\\timing': (toggle_timing, ['\\timing', 'Toggle timing of commands.']),
            '\\dt': (list_tables, ['\\dt[+] [pattern]', 'List tables.']),
            '\\di': (list_indexes, ['\\di[+] [pattern]', 'List indexes.']),
            '\\dv': (list_views, ['\\dv[+] [pattern]', 'List views.']),
            '\\ds': (list_sequences, ['\\ds[+] [pattern]', 'List sequences.']),
            '\\df': (list_functions, ['\\df[+] [pattern]', 'List functions.']),
            '\\dT': (list_datatypes, ['\dT[S+] [pattern]', 'List data types']),
            '\e': (dummy_command, ['\e [file]', 'Edit the query buffer (or file) with external editor.']),
            '\ef': (in_progress, ['\ef [funcname [line]]', 'Not yet implemented.']),
            '\sf': (in_progress, ['\sf[+] funcname', 'Not yet implemented.']),
            '\z': (in_progress, ['\z [pattern]', 'Not yet implemented.']),
            '\do': (in_progress, ['\do[S] [pattern]', 'Not yet implemented.']),
            '\\n': (execute_named_query, ['\\n[+] [name]', 'List or execute named queries.']),
            '\\ns': (save_named_query, ['\\ns [name [query]]', 'Save a named query.']),
            '\\nd': (delete_named_query, ['\\nd [name]', 'Delete a named query.']),
            }

# Commands not shown via help.
HIDDEN_COMMANDS = {
            'describe': (describe_table_details, ['DESCRIBE [pattern]', '']),
            }

@export
def parse_special_command(sql):
    command, _, arg = sql.partition(' ')
    verbose = '+' in command

    command = command.strip().replace('+', '')
    return (command, verbose, arg.strip())

@export
def execute(cur=None, sql='', db_obj=None):
    """Execute a special command and return the results. If the special command
    is not supported a KeyError will be raised.
    """
    command, verbose, arg = parse_special_command(sql)

    # Look up the command in the case-sensitive dict, if it's not there look in
    # non-case-sensitive dict. If not there either, throw a KeyError exception.
    try:
        command_executor = COMMANDS[command][0]
    except KeyError:
        command_executor = HIDDEN_COMMANDS[command.lower()][0]

    # If the command executor is a function, then call the function with the
    # args. If it's a string, then assume it's an SQL command and run it.
    if callable(command_executor):
        return command_executor(cur, arg, verbose)
    elif isinstance(command_executor, str):
        cur.execute(command_executor)
        if cur.description:
            headers = [x[0] for x in cur.description]
            return [(None, cur, headers, cur.statusmessage)]
        else:
            return [(None, None, None, cur.statusmessage)]