import re
import logging

def clean_metadata(schema):
    """
    Clean and standardize extracted metadata.
      - Standardize table and column names (e.g., lower-case and remove underscores).
      - Filter out system tables if needed.
    Returns a cleaned schema dictionary.
    """
    cleaned_schema = {}
    for table_name, data in schema.items():
        # Filter out system tables (e.g., those starting with 'sys')
        if table_name.lower().startswith("sys"):
            continue
        
        # Standardize table name
        clean_table_name = table_name.lower()
        cleaned_schema[clean_table_name] = {}

        # Clean columns: lower-case and remove underscores for clarity
        columns = data.get("columns", [])
        cleaned_columns = []
        for col in columns:
            col_name = col["name"].lower()
            col_name = re.sub(r"_", " ", col_name).strip()
            cleaned_columns.append({"name": col_name, "data_type": col["data_type"]})
        cleaned_schema[clean_table_name]["columns"] = cleaned_columns

        # Clean primary keys
        primary_keys = [pk.lower() for pk in data.get("primary_keys", [])]
        cleaned_schema[clean_table_name]["primary_keys"] = primary_keys

        # Clean foreign keys
        foreign_keys = data.get("foreign_keys", [])
        cleaned_fks = []
        for fk in foreign_keys:
            cleaned_fk = {
                "fk_name": fk["fk_name"].lower(),
                "parent_column": fk["parent_column"].lower(),
                "referenced_table": fk["referenced_table"].lower(),
                "referenced_column": fk["referenced_column"].lower()
            }
            cleaned_fks.append(cleaned_fk)
        cleaned_schema[clean_table_name]["foreign_keys"] = cleaned_fks

    return cleaned_schema 