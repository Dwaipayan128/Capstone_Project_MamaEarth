# Mamaearth Returns & Growth Intelligence Pipeline

**Program:** Data Analytics with AI & Gen AI · E&ICT Academy IIT Roorkee  
**Architecture:** 3-Tier Pipeline (SQL Relational Store → Python Wrangling & EDA → GenAI Narrative)

---

## 1. Repository Structure
├── README.md                           # Master pipeline documentation & execution guide
├── data/
│   ├── customers.csv                   # Raw customer table (45 rows)
│   ├── products.csv                    # Raw products catalog (16 rows)
│   └── orders.csv                      # Raw transaction logs with duplicates & missing fields (180 rows)
├── sql/
│   ├── schema.sql                      # DDL schema definition with ANSI foreign keys
│   ├── seed_data.sql                   # Import loader & null normalization script
│   └── reports.sql                     # Task 3 analytical reporting queries with expected outputs
├── analysis/
│   ├── clean_and_eda.py                # Standalone pandas pipeline & findings.json exporter
│   └── visualize.py                    # Production visualization generator
├── visualizations/
│   ├── return_rate_by_payment.png      # Payment return rate comparison chart
│   └── monthly_revenue_trend.png       # Outlier-adjusted monthly revenue trend chart
└── narrator/
├── findings.json                   # Verified cross-layer metrics payload
├── generate_narrative.py           # Gemini GenAI narrator with offline fallback
└── sample_output.txt               # Verified benchmark execution output
