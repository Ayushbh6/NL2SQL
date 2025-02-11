import openai

def generate_summary(table_name, text, llm_config):
    """
    Generate a brief summary for the schema metadata of a table using the LLM.
    """
    openai.api_key = llm_config["api_key"]
    prompt = (
        f"Please provide a highly detailed, microscopic summary for the schema of table '{table_name}'. "
        f"Your summary must include a thorough analysis of the table's structure including important columns, "
        f"join relationships (foreign keys), primary keys, indexes, check and default constraints, triggers, "
        f"and any additional metadata provided. Ensure that no relevant detail is omitted.\n\n"
        f"Metadata:\n\n{text}\n\nDetailed Summary:"
    )
    try:
        response = openai.ChatCompletion.create(
            model=llm_config.get("model", "o3-mini"),
            messages=[
                {"role": "system", "content": "You are a highly experienced database schema expert who provides a detailed and microscopic analysis of table schemas. Capture all aspects including table details, important columns, join conditions, constraints, indexes, and triggers."},
                {"role": "user", "content": prompt}
            ]
        )
        summary = response.choices[0].message.content.strip()
    except Exception as e:
        summary = f"Error generating summary: {e}"
    return summary

def generate_mini_summary(table_name, text, llm_config):
    """
    Generate a mini summarized version of the given summary.
    This condenses the key points so that it can be used as context for subsequent LLM calls.
    """
    openai.api_key = llm_config["api_key"]
    prompt = (
        f"Please condense the following summary for table '{table_name}' into key bullet points "
        f"highlighting the essential information:\n\n{text}\n\nMini Summary:"
    )
    try:
        response = openai.ChatCompletion.create(
            model=llm_config.get("model", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are an assistant that extracts the key points from a summary."},
                {"role": "user", "content": prompt}
            ]
        )
        mini_summary = response.choices[0].message.content.strip()
    except Exception as e:
        mini_summary = f"Error generating mini summary: {e}"
    return mini_summary 