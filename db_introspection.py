import pyodbc
import logging

def get_db_connection(db_config):
    """
    Establish a connection to the SQL Server database using pyodbc.
    """
    try:
        conn_str = (
            f"DRIVER={{{db_config['driver']}}};"
            f"SERVER={db_config['server']};"
            f"DATABASE={db_config['database']};"
            f"UID={db_config['username']};"
            f"PWD={db_config['password']};"
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        return None

def extract_schema(conn):
    """
    Extract comprehensive database schema information for each table.
    This includes:
      - Detailed column metadata (data type, length, precision, nullable, identity, computed)
      - Primary keys
      - Foreign keys
      - Indexes (with unique and primary key information)
      - Check constraints
      - Default constraints
      - Triggers
    Returns a dictionary with table names as keys.
    """
    schema = {}

    # Retrieve list of user tables
    table_query = "SELECT name FROM sys.tables;"
    cursor = conn.cursor()
    cursor.execute(table_query)
    tables = cursor.fetchall()

    for table in tables:
        table_name = table.name
        schema[table_name] = {}

        # 1. Retrieve detailed columns metadata
        column_query = f"""
            SELECT c.name AS column_name, 
                   t.name AS data_type, 
                   c.max_length, 
                   c.precision, 
                   c.scale, 
                   c.is_nullable, 
                   c.is_identity, 
                   c.is_computed
            FROM sys.columns c
            JOIN sys.types t ON c.user_type_id = t.user_type_id
            WHERE c.object_id = OBJECT_ID('{table_name}');
        """
        cursor.execute(column_query)
        columns = cursor.fetchall()
        schema[table_name]["columns"] = [
            {
                "name": col.column_name,
                "data_type": col.data_type,
                "max_length": col.max_length,
                "precision": col.precision,
                "scale": col.scale,
                "is_nullable": bool(col.is_nullable),
                "is_identity": bool(col.is_identity),
                "is_computed": bool(col.is_computed)
            }
            for col in columns
        ]

        # 2. Retrieve primary keys
        pk_query = f"""
            SELECT c.name AS column_name
            FROM sys.indexes i
            JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
            JOIN sys.columns c ON ic.object_id = c.object_id AND c.column_id = ic.column_id
            WHERE i.is_primary_key = 1 AND i.object_id = OBJECT_ID('{table_name}');
        """
        cursor.execute(pk_query)
        pks = cursor.fetchall()
        schema[table_name]["primary_keys"] = [pk.column_name for pk in pks]

        # 3. Retrieve foreign keys
        fk_query = f"""
            SELECT
                f.name AS fk_name,
                COL_NAME(fc.parent_object_id, fc.parent_column_id) AS parent_column,
                OBJECT_NAME (f.referenced_object_id) AS referenced_table,
                COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS referenced_column
            FROM
                sys.foreign_keys AS f
            INNER JOIN
                sys.foreign_key_columns AS fc 
                  ON f.OBJECT_ID = fc.constraint_object_id
            WHERE f.parent_object_id = OBJECT_ID('{table_name}');
        """
        cursor.execute(fk_query)
        fks = cursor.fetchall()
        schema[table_name]["foreign_keys"] = [
            {
                "fk_name": fk.fk_name,
                "parent_column": fk.parent_column,
                "referenced_table": fk.referenced_table,
                "referenced_column": fk.referenced_column
            }
            for fk in fks
        ]

        # 4. Retrieve indexes (grouping columns per index)
        indexes_query = f"""
            SELECT ind.name AS index_name, 
                   col.name AS column_name, 
                   ind.is_unique, 
                   ind.is_primary_key
            FROM sys.indexes ind
            JOIN sys.index_columns ic ON ind.object_id = ic.object_id AND ind.index_id = ic.index_id
            JOIN sys.columns col ON ic.object_id = col.object_id AND ic.column_id = col.column_id
            WHERE ind.object_id = OBJECT_ID('{table_name}') AND ind.name IS NOT NULL;
        """
        cursor.execute(indexes_query)
        indexes_rows = cursor.fetchall()
        indexes_dict = {}
        for row in indexes_rows:
            idx_name = row.index_name
            if idx_name not in indexes_dict:
                indexes_dict[idx_name] = {
                    "index_name": idx_name,
                    "is_unique": bool(row.is_unique),
                    "is_primary_key": bool(row.is_primary_key),
                    "columns": []
                }
            indexes_dict[idx_name]["columns"].append(row.column_name)
        schema[table_name]["indexes"] = list(indexes_dict.values())

        # 5. Retrieve check constraints
        check_constraints_query = f"""
            SELECT cc.name AS constraint_name, cc.definition
            FROM sys.check_constraints cc
            WHERE cc.parent_object_id = OBJECT_ID('{table_name}');
        """
        cursor.execute(check_constraints_query)
        check_constraints = cursor.fetchall()
        schema[table_name]["check_constraints"] = [
            {"constraint_name": cc.constraint_name, "definition": cc.definition} for cc in check_constraints
        ]

        # 6. Retrieve default constraints for columns
        default_constraints_query = f"""
            SELECT col.name AS column_name, dc.definition
            FROM sys.columns col
            JOIN sys.default_constraints dc ON col.default_object_id = dc.object_id
            WHERE col.object_id = OBJECT_ID('{table_name}');
        """
        cursor.execute(default_constraints_query)
        default_constraints = cursor.fetchall()
        schema[table_name]["default_constraints"] = [
            {"column_name": dc.column_name, "definition": dc.definition} for dc in default_constraints
        ]

        # 7. Retrieve triggers defined on the table
        triggers_query = f"""
            SELECT t.name AS trigger_name, t.is_disabled
            FROM sys.triggers t
            WHERE t.parent_id = OBJECT_ID('{table_name}');
        """
        cursor.execute(triggers_query)
        triggers = cursor.fetchall()
        schema[table_name]["triggers"] = [
            {"trigger_name": trig.trigger_name, "is_disabled": bool(trig.is_disabled)} for trig in triggers
        ]

    return schema 