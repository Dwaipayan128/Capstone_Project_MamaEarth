# Mamaearth Returns & Growth Intelligence Pipeline

A three-tier data analytics project developed as part of the **Data Analytics with AI & Gen AI programme at E&ICT Academy, IIT Roorkee**.

The pipeline integrates SQLite, SQL, Python, and Generative AI for relational data management, data wrangling, exploratory data analysis, visualisation, and narrative generation.

## Architecture

1. **SQL Layer:** Relational database initialisation, data loading, normalisation, and analytical reporting using SQLite.
2. **Python Layer:** Data wrangling, exploratory data analysis (EDA), and analytical processing.
3. **Generative AI Layer:** Narrative generation based on analytical outputs.

## Repository Structure

```text
Capstone_Project_MamaEarth/
├── analysis/          # Data analysis
├── data/              # Source datasets
├── narrator/          # Narrative generation
├── sql/               # Database schema and SQL scripts
├── visualizations/    # Data visualisations
└── README.md          # Project documentation
```

## Prerequisites

- SQLite command-line interface
- Python
- Python libraries required by the project scripts
- Access to the project datasets

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Dwaipayan128/Capstone_Project_MamaEarth.git
cd Capstone_Project_MamaEarth
```

### 2. Verify the project files

Ensure the `data/`, `sql/`, `analysis/`, `narrator/`, and `visualizations/` directories are present.

Ensure the source CSV files are available in `data/`:

- `customers.csv`
- `products.csv`
- `orders.csv`

### 3. Initialise the SQLite database

Run the following command from the repository root:

```bash
sqlite3 mamaearth.db < sql/schema.sql
```

This creates and initialises the database using the schema defined in `sql/schema.sql`.

### 4. Import the source datasets

Import the CSV files into their respective tables:

```bash
sqlite3 mamaearth.db -cmd ".mode csv" ".import data/customers.csv customers"
sqlite3 mamaearth.db -cmd ".mode csv" ".import data/products.csv products"
sqlite3 mamaearth.db -cmd ".mode csv" ".import data/orders.csv orders"
```

The target tables must exist before importing the datasets. Follow the schema and CSV header conventions defined by the project.

### 5. Execute SQL scripts

Run the data seeding and analytical reporting scripts:

```bash
sqlite3 mamaearth.db < sql/seed_data.sql
sqlite3 mamaearth.db < sql/reports.sql
```

These scripts perform the database operations and reporting defined in the SQL layer.

## Execution Order

Execute the pipeline in the following order:

1. **Database initialisation:** Create the SQLite database and tables.
2. **Data loading:** Import the customer, product, and order datasets.
3. **SQL processing:** Execute the seeding, normalisation, and reporting scripts.
4. **Python analysis:** Run the applicable scripts in `analysis/` for data wrangling and exploratory analysis.
5. **Visualisation:** Generate or review the analytical visualisations in `visualizations/`.
6. **Narrative generation:** Execute the applicable components in `narrator/` to generate analytical narratives.

Run Python components using their actual script or notebook filenames. Install any required dependencies before execution.

## Technology Stack

| Technology | Purpose |
|---|---|
| SQLite | Relational database management |
| SQL | Data loading, database operations, and analytical reporting |
| Python | Data wrangling and exploratory data analysis |
| Generative AI | Narrative generation |
| Data visualisation tools | Graphical representation of analytical results |

## Data

The project uses three datasets:

- **Customers:** Customer attributes and acquisition information.
- **Products:** Product details, categories, and prices.
- **Orders:** Transaction records, quantities, discounts, payment methods, ratings, and return status.

Source data should be preserved separately from cleaned or transformed data. Apply data-cleaning operations through the designated processing scripts.

## Repository

[GitHub — Capstone_Project_MamaEarth](https://github.com/Dwaipayan128/Capstone_Project_MamaEarth)
