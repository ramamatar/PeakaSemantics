import os
import json
from sqlglot import transpile
import sqlglot.errors
from sqlglot import exp
from sqlglot.helper import logger as helper_logger

helper_logger.disabled = True

def custom_transformer(node):
    if isinstance(node, exp.ToNumber):
        return exp.Cast(this=node.this, to=exp.DataType(this=exp.DataType.Type.DECIMAL))
    if isinstance(node, exp.RegexpExtract):
        return exp.RegexpExtract(
            this=node.this,
            expression=node.expression,
            position=None,
            occurrence=None,
            parameters=None
        )
    return node

SQL_DIR = "sql"
RESULT_DIR = "exec_result"
INSTRUCTION_FILE = "spider2-snow.jsonl"
OUTPUT_FILE = "output.json"

instruction_map = {}
with open(INSTRUCTION_FILE, 'r', encoding="utf-8") as f:
    for line in f:
        entry = json.loads(line)
        instruction_id = entry.get("instance_id")
        instruction = entry.get("instruction")
        database = entry.get("db_id")
        if instruction_id and instruction:
            instruction_map[instruction_id] = (instruction, database)

output_data = []

for filename in os.listdir(SQL_DIR):
    if not filename.endswith(".sql"):
        continue

    instance_id = os.path.splitext(filename)[0]

    if instance_id not in instruction_map:
        continue

    sql_path = os.path.join(SQL_DIR, filename)

    try:
        with open(sql_path, "r", encoding="utf-8") as sql_file:
            original_sql = sql_file.read().strip()
    except Exception:
        continue

    try:
        transpiled_sql_list = transpile(
            sql=original_sql,
            read="snowflake",
            write="trino",
            identity=True,
            error_level=sqlglot.errors.ErrorLevel.WARN,
            transforms=[custom_transformer]
        )
        transpiled_sql = transpiled_sql_list[0] if transpiled_sql_list else original_sql
    except Exception:
        transpiled_sql = original_sql

    instruction, database = instruction_map[instance_id]

    output_data.append({
        "sql_query": transpiled_sql,
        "instruction": instruction,
        "database": database,
        "result-file": instance_id
    })

with open(OUTPUT_FILE, "w", encoding="utf-8") as out_file:
    json.dump(output_data, out_file, indent=2, ensure_ascii=False)
