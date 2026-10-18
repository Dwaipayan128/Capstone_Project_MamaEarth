# Mamaearth Returns & Growth Intelligence Pipeline

**Program:** Data Analytics with AI & Gen AI · E&ICT Academy IIT Roorkee  
**Architecture:** 3-Tier Pipeline (SQL Relational Store → Python Wrangling & EDA → GenAI Narrative)

---

## 1. Repository Structure
---

## 2. End-to-End Pipeline Execution Order

### Step 1: Relational Database & SQL Layer (Part 1)
Initialize the SQLite relational database, load seed data, and execute analytical reports:
```bash
# Initialize SQLite database
sqlite3 mamaearth.db < sql/schema.sql

# Import seed CSVs into tables
sqlite3 mamaearth.db -cmd ".mode csv" ".import data/customers.csv customers"
sqlite3 mamaearth.db -cmd ".mode csv" ".import data/products.csv products"
sqlite3 mamaearth.db -cmd ".mode csv" ".import data/orders.csv orders"

# Run normalization and reporting queries
sqlite3 mamaearth.db < sql/seed_data.sql
sqlite3 mamaearth.db < sql/reports.sql
