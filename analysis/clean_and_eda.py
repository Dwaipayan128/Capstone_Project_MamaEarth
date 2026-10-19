"""
clean_and_eda.py
Mamaearth Growth & Returns Intelligence Pipeline - Part 2
Independent pandas-driven data cleaning, reconciliation, outlier detection, and EDA.
"""

import os
import json
import pandas as pd
import numpy as np

# Set console display precision
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def main():
    print("=" * 80)
    print("MAMAEARTH GROWTH ANALYTICS: PIPELINE PART 2 (CLEANING & EDA)")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # Task 1: Load and inspect
    # -------------------------------------------------------------------------
    print("\n--- TASK 1: Load and Inspect ---")
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    orders_path = os.path.join(data_dir, "orders.csv")
    customers_path = os.path.join(data_dir, "customers.csv")
    products_path = os.path.join(data_dir, "products.csv")

    orders = pd.read_csv(orders_path)
    customers = pd.read_csv(customers_path)
    products = pd.read_csv(products_path)

    print(f"Raw orders.shape: {orders.shape}")
    assert orders.shape == (180, 9), f"Expected (180, 9), got {orders.shape}"

    # -------------------------------------------------------------------------
    # Task 2: Standardize payment_method casing
    # -------------------------------------------------------------------------
    print("\n--- TASK 2: Standardize payment_method Casing ---")
    raw_payment_methods = orders['payment_method'].unique().tolist()
    print(f"Distinct raw payment methods ({len(raw_payment_methods)}): {raw_payment_methods}")
    assert len(raw_payment_methods) == 7, f"Expected 7 distinct raw methods, found {len(raw_payment_methods)}"

    orders['payment_method'] = orders['payment_method'].astype(str).str.strip().str.upper()
    cleaned_counts = orders['payment_method'].value_counts().to_dict()
    print("Standardized payment_method counts:", cleaned_counts)
    assert cleaned_counts == {'CARD': 70, 'UPI': 55, 'COD': 55}, f"Unexpected counts: {cleaned_counts}"

    # -------------------------------------------------------------------------
    # Task 3: Remove duplicate orders
    # -------------------------------------------------------------------------
    print("\n--- TASK 3: Remove Duplicate Orders ---")
    natural_key = [
        'customer_id', 'product_id', 'order_date', 'quantity', 
        'discount_pct', 'payment_method', 'rating', 'returned'
    ]
    duplicate_mask = orders.duplicated(subset=natural_key, keep='first')
    dropped_orders = orders[duplicate_mask]
    dropped_ids = dropped_orders['order_id'].tolist()
    print(f"Duplicates detected: {len(dropped_ids)}")
    print(f"Dropped order_ids: {dropped_ids}")
    assert dropped_ids == ['O0176', 'O0177', 'O0178', 'O0179', 'O0180'], f"Unexpected dropped IDs: {dropped_ids}"

    orders_clean = orders[~duplicate_mask].copy()
    print(f"Cleaned orders shape: {orders_clean.shape}")
    assert orders_clean.shape == (175, 9), f"Expected (175, 9), got {orders_clean.shape}"

    # -------------------------------------------------------------------------
    # Task 4: Impute missing values
    # -------------------------------------------------------------------------
    print("\n--- TASK 4: Impute Missing Values ---")
    discount_missing_count = orders_clean['discount_pct'].isna().sum()
    print(f"Missing discount_pct rows before imputation: {discount_missing_count}")
    assert discount_missing_count == 12, f"Expected 12 missing discounts, found {discount_missing_count}"
    orders_clean['discount_pct'] = orders_clean['discount_pct'].fillna(0).astype(float)

    rating_missing_count = orders_clean['rating'].isna().sum()
    rating_median = float(orders_clean['rating'].median())
    print(f"Missing rating rows before imputation: {rating_missing_count}")
    print(f"Median rating on non-null rows: {rating_median}")
    assert rating_missing_count == 15, f"Expected 15 missing ratings, found {rating_missing_count}"
    assert rating_median == 3.0, f"Expected median rating of 3.0, got {rating_median}"
    orders_clean['rating'] = orders_clean['rating'].fillna(rating_median).astype(float)

    null_check = orders_clean[['discount_pct', 'rating']].isnull().sum().to_dict()
    print(f"Post-imputation null counts: {null_check}")
    assert null_check == {'discount_pct': 0, 'rating': 0}

    # -------------------------------------------------------------------------
    # Task 5: Merge and reconcile against Part 1
    # -------------------------------------------------------------------------
    print("\n--- TASK 5: Merge and Reconcile against Part 1 ---")
    merged_clean = orders_clean.merge(products, on='product_id', how='left')
    merged_clean = merged_clean.merge(customers, on='customer_id', how='left')

    merged_clean['order_value'] = (
        merged_clean['quantity'] * merged_clean['price'] * (1.0 - merged_clean['discount_pct'] / 100.0)
    )
    cleaned_total_revenue = round(float(merged_clean['order_value'].sum()), 2)
    print(f"Total Revenue across 175 cleaned rows: INR {cleaned_total_revenue:.2f}")
    assert cleaned_total_revenue == 97358.30, f"Expected 97358.30, got {cleaned_total_revenue}"

    # Independent check on dropped rows:
    dropped_with_price = dropped_orders.merge(products, on='product_id', how='left')
    dropped_with_price['discount_pct'] = dropped_with_price['discount_pct'].fillna(0)
    dropped_value = round(float((
        dropped_with_price['quantity'] * dropped_with_price['price'] * (1.0 - dropped_with_price['discount_pct'] / 100.0)
    ).sum()), 2)

    raw_total_revenue = 99860.20
    reconciliation_delta = round(raw_total_revenue - cleaned_total_revenue, 2)

    print("\n" + "=" * 60)
    print("RECONCILIATION AUDIT NOTE:")
    print(
        f"The gross revenue from the raw Part 1 SQL reports was INR {raw_total_revenue:.2f}. "
        f"The cleaned dataset reports INR {cleaned_total_revenue:.2f}, creating an exact variance of "
        f"INR {reconciliation_delta:.2f}. An independent valuation of the 5 dropped double-submit "
        f"duplicate orders (O0176, O0177, O0178, O0179, O0180) totals exactly INR {dropped_value:.2f}. "
        f"This proves that the entire discrepancy is strictly attributable to synthetic multi-click "
        f"duplicate transaction telemetry, and confirms that promo-code discount (0%) and customer rating "
        f"imputations (median 3.0) had zero distortionary impact on final transactional revenue."
    )
    print("=" * 60)
    assert reconciliation_delta == 2501.90, f"Expected delta of 2501.90, got {reconciliation_delta}"
    assert dropped_value == 2501.90, f"Expected dropped value of 2501.90, got {dropped_value}"

    # -------------------------------------------------------------------------
    # Task 6: IQR outlier detection on quantity
    # -------------------------------------------------------------------------
    print("\n--- TASK 6: IQR Outlier Detection on Quantity ---")
    q1 = float(merged_clean['quantity'].quantile(0.25))
    q3 = float(merged_clean['quantity'].quantile(0.75))
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    print(f"Q1: {q1}, Q3: {q3}, IQR: {iqr}, Lower Bound: {lower_bound}, Upper Bound: {upper_bound}")
    assert (q1, q3, iqr, lower_bound, upper_bound) == (1.0, 2.0, 1.0, -0.5, 3.5)

    merged_clean['is_outlier'] = (merged_clean['quantity'] < lower_bound) | (merged_clean['quantity'] > upper_bound)
    outliers = merged_clean[merged_clean['is_outlier']][['order_id', 'quantity', 'order_date', 'product_id']]
    outlier_ids = sorted(outliers['order_id'].tolist())
    print(f"Detected Outlier Rows ({len(outliers)}):")
    print(outliers.to_string(index=False))
    assert outlier_ids == ['O0011', 'O0098'], f"Expected ['O0011', 'O0098'], got {outlier_ids}"

    # -------------------------------------------------------------------------
    # Task 7: Hypothesis: Does COD have a higher return rate?
    # -------------------------------------------------------------------------
    print("\n--- TASK 7: Hypothesis Testing: COD vs Return Rate ---")
    print("Hypothesis: Orders placed via Cash On Delivery (COD) suffer a substantially higher return rate than digital payments.")
    payment_stats = merged_clean.groupby('payment_method')['returned'].agg(['count', 'mean'])
    payment_stats['return_rate_pct'] = (payment_stats['mean'] * 100).round(1)
    print(payment_stats[['count', 'return_rate_pct']])

    rates = payment_stats['return_rate_pct'].to_dict()
    assert rates['CARD'] == 14.7, f"Expected CARD 14.7, got {rates['CARD']}"
    assert rates['COD'] == 44.4, f"Expected COD 44.4, got {rates['COD']}"
    assert rates['UPI'] == 18.9, f"Expected UPI 18.9, got {rates['UPI']}"
    print("Hypothesis: Confirmed (COD return rate of 44.4% is ~3x higher than Card).")

    # -------------------------------------------------------------------------
    # Task 8: Multi-level segmentation
    # -------------------------------------------------------------------------
    print("\n--- TASK 8: Multi-Level Segmentation (Payment Method x City Tier) ---")
    segment_stats = merged_clean.groupby(['payment_method', 'city_tier'])['returned'].agg(['count', 'sum', 'mean'])
    segment_stats['return_rate_pct'] = (segment_stats['mean'] * 100).round(1)
    print(segment_stats[['count', 'sum', 'return_rate_pct']])

    tier1_cod = segment_stats.loc[('COD', 1), 'return_rate_pct']
    tier2_cod = segment_stats.loc[('COD', 2), 'return_rate_pct']
    tier1_cod_count = segment_stats.loc[('COD', 1), 'count']
    tier2_cod_count = segment_stats.loc[('COD', 2), 'count']

    assert (tier1_cod_count, tier1_cod) == (32, 37.5), f"Expected (32, 37.5), got ({tier1_cod_count}, {tier1_cod})"
    assert (tier2_cod_count, tier2_cod) == (22, 54.5), f"Expected (22, 54.5), got ({tier2_cod_count}, {tier2_cod})"
    print(f"Highest-risk segment: COD + Tier-2 cities at {tier2_cod}% return rate.")

    # -------------------------------------------------------------------------
    # Task 9: Correlation analysis
    # -------------------------------------------------------------------------
    print("\n--- TASK 9: Correlation Analysis ---")
    corr_cols = ['rating', 'returned', 'discount_pct', 'quantity']
    corr_matrix = merged_clean[corr_cols].corr()
    print("Correlation Matrix:")
    print(corr_matrix.round(4))

    def get_band(r):
        abs_r = abs(r)
        if abs_r < 0.20:
            return "negligible"
        elif abs_r < 0.40:
            return "weak"
        elif abs_r < 0.70:
            return "moderate"
        else:
            return "strong"

    pairs = [
        ('rating', 'returned'), ('rating', 'discount_pct'), ('rating', 'quantity'),
        ('returned', 'discount_pct'), ('returned', 'quantity'), ('discount_pct', 'quantity')
    ]
    for c1, c2 in pairs:
        r_val = corr_matrix.loc[c1, c2]
        band = get_band(r_val)
        print(f"Pair ({c1}, {c2}): r = {r_val:.4f} -> {band}")
        assert band == "negligible", f"Expected negligible for ({c1}, {c2}), got {band}"

    discount_return_corr = corr_matrix.loc['discount_pct', 'returned']
    print(f"Hypothesis 'higher discounts reduce returns': Busted (r = {discount_return_corr:.4f} ≈ -0.09).")

    # -------------------------------------------------------------------------
    # Task 10: Outlier-corrected time series
    # -------------------------------------------------------------------------
    print("\n--- TASK 10: Outlier-Corrected Time Series ---")
    merged_clean['order_date'] = pd.to_datetime(merged_clean['order_date'])
    merged_clean['year_month'] = merged_clean['order_date'].dt.to_period('M').astype(str)

    monthly_raw = merged_clean.groupby('year_month')['order_value'].sum().round(2).to_dict()
    monthly_corrected = (
        merged_clean[~merged_clean['is_outlier']]
        .groupby('year_month')['order_value'].sum().round(2).to_dict()
    )

    print("Monthly Revenue (Raw including bulk outliers):")
    for m, val in monthly_raw.items():
        print(f"  {m}: INR {val:.2f}")

    print("\nMonthly Revenue (Outlier-Corrected):")
    for m, val in monthly_corrected.items():
        print(f"  {m}: INR {val:.2f}")

    assert monthly_raw['2026-01'] == 29582.10
    assert monthly_raw['2026-06'] == 11615.40
    assert monthly_corrected == {
        '2026-01': 11637.10,
        '2026-02': 13195.50,
        '2026-03': 20318.90,
        '2026-04': 9495.30,
        '2026-05': 13151.10,
        '2026-06': 11615.40
    }
    print(
        "Observation: January's apparent lead (INR 29,582.10) is an artifact of the two bulk "
        "quantity outlier orders (O0011 on 2026-01-28, O0098 on 2026-01-10). Once filtered, "
        "March (2026-03 at INR 20,318.90) is identified as the genuine operational peak month."
    )

    # -------------------------------------------------------------------------
    # Part 3 Task 1: Export findings.json
    # -------------------------------------------------------------------------
    print("\n--- EXPORTING FINDINGS TO narrator/findings.json ---")
    narrator_dir = os.path.join(os.path.dirname(__file__), "..", "narrator")
    os.makedirs(narrator_dir, exist_ok=True)
    findings_path = os.path.join(narrator_dir, "findings.json")

    findings = {
        "cleaned_total_revenue_inr": cleaned_total_revenue,
        "raw_total_revenue_inr": raw_total_revenue,
        "duplicate_reconciliation_delta_inr": reconciliation_delta,
        "return_rate_by_payment": {
            "COD": rates['COD'],
            "CARD": rates['CARD'],
            "UPI": rates['UPI']
        },
        "highest_risk_segment": {
            "payment_method": "COD",
            "city_tier": 2,
            "return_rate_pct": tier2_cod
        },
        "true_peak_month": {
            "month": "2026-03",
            "revenue_inr": monthly_corrected['2026-03']
        },
        "outlier_inflated_month": {
            "month": "2026-01",
            "apparent_revenue_inr": monthly_raw['2026-01'],
            "corrected_revenue_inr": monthly_corrected['2026-01']
        }
    }

    with open(findings_path, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2)

    print(f"Successfully generated {findings_path} with verified pipeline metrics.")

if __name__ == "__main__":
    main()
