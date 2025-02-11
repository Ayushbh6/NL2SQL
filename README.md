# NL2SQL Project

A Natural Language to SQL query generator that handles complex database schemas with hundreds of tables.

## Features

- Database schema introspection
- Metadata cleaning and standardization
- Token-aware schema compression
- LLM-powered schema summarization
- Support for handling large schemas through chunking

## Setup

1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/NL2SQL.git
cd NL2SQL
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure the database connection
- Copy `config.json.example` to `config.json`
- Update the configuration with your database credentials

## Usage

Run the main script:
```bash
python main.py
```

## Configuration

The system uses a `config.json` file for configuration. See `config.json.example` for the required format.

## License

MIT