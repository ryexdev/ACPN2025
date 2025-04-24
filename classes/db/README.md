# SQLite Database

This directory contains a SQLite database for storing product information and generation logs.

## Database Structure

The database contains the following tables:

### Products Table

Stores information about different pie products:

- `id`: Primary key
- `name`: Name of the product
- `type`: Type of pie (fruit, nut, savory, cream, etc.)
- `ingredients`: List of ingredients
- `occasion`: Suitable occasion for the pie
- `description`: Detailed description of the product
- `created_at`: Timestamp of when the record was created

### Generation Logs Table

Tracks AI-generated content for products:

- `id`: Primary key
- `product_id`: Foreign key referencing the products table
- `prompt`: Prompt used for generation
- `engine`: AI engine used (openai, ollama, etc.)
- `result`: Generated content
- `created_at`: Timestamp of when the generation was created

## Usage

```python
# Import the database utility
from pages.classes.db import db

# Get all products
products = db.get_products()

# Get a specific product
product = db.get_product_by_id(1)

# Add a generation log
db.add_generation_log(
    product_id=1,
    prompt="Generate a description...",
    engine="openai",
    result="Generated content..."
)

# Get generation logs for a product
logs = db.get_generation_logs(product_id=1)
```

## Database Initialization

The database is automatically created and populated with example data when 
you run the `pages/local_db_test.py` script:

```
python pages/local_db_test.py
```

The example data is loaded from `pages/classes/data/example_products.sql`. 