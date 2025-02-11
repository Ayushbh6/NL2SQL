import json
import logging
import os

from db_introspection import get_db_connection, extract_schema, build_join_flows
from metadata_cleaner import clean_metadata
from token_utils import count_tokens, chunk_text
from llm_client import generate_summary, generate_mini_summary

def load_config():
    # Load configuration from config.json
    with open("config.json", "r") as f:
        config = json.load(f)
    return config

def save_optimized_schema(schema, filename="optimized_schema.json"):
    with open(filename, "w") as f:
        json.dump(schema, f, indent=4)

def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Loading configuration...")
    config = load_config()

    logging.info("Connecting to database...")
    conn = get_db_connection(config["db"])
    if not conn:
        logging.error("Database connection failed")
        return

    logging.info("Extracting schema from database...")
    schema = extract_schema(conn)
    conn.close()

    logging.info("Cleaning and standardizing metadata...")
    cleaned_schema = clean_metadata(schema)

    logging.info("Processing schema: token counting and LLM summarization...")
    optimized_schema = {}
    for table_name, table_data in cleaned_schema.items():
        # Convert table metadata to JSON string (for token counting)
        table_text = json.dumps(table_data)
        token_count = count_tokens(table_text, config["token"]["llm_encoding"])
        logging.info(f"Table '{table_name}' token count: {token_count}")

        if token_count > config["token"]["max_tokens"]:
            logging.info(f"Table '{table_name}' exceeds token limit, chunking text...")
            # Process chunk by chunk and build a cumulative summary.
            chunks = list(chunk_text(table_text, config["token"]["max_tokens"], config["token"]["llm_encoding"]))
            summary = ""
            for i, chunk in enumerate(chunks):
                if i == 0:
                    prompt_text = chunk
                else:
                    # Generate a mini summary (condensed version) of the current summary
                    mini_summary = generate_mini_summary(table_name, summary, config["llm"])
                    prompt_text = mini_summary + "\n" + chunk
                new_chunk_summary = generate_summary(table_name, prompt_text, config["llm"])
                if i == 0:
                    summary = new_chunk_summary
                else:
                    summary = mini_summary + f"\n[Summary of chunk {i+1}]: " + new_chunk_summary
            optimized_schema[table_name] = summary.strip()
        else:
            summary = generate_summary(table_name, table_text, config["llm"])
            optimized_schema[table_name] = summary

    # Generate join flow descriptions from the cleaned schema.
    join_flows = build_join_flows(cleaned_schema)

    # Append flows to the final output dictionary.
    final_output = {
         "optimized_schema": optimized_schema,
         "join_flows": join_flows
    }

    output_file = "optimized_schema.json"
    logging.info(f"Saving optimized schema and join flows to {output_file}...")
    save_optimized_schema(final_output, output_file)
    logging.info("Process completed successfully.")

if __name__ == "__main__":
    main() 