"""
visualize.py
Mamaearth Growth & Returns Intelligence Pipeline - Part 2 Task 11
Generates standalone production visual plots saved to visualizations/.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

def generate_visualizations():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    vis_dir = os.path.join(os.path.dirname(__file__), "..", "visualizations")
    os.makedirs(vis_dir, exist_ok=True)

    orders = pd.read_csv(os.path.join(data_dir, "orders.csv"))
    products = pd.read_csv(os.path.join(data_dir, "products.csv"))

    # Cleaning pipeline matching clean_and_eda.py
    orders['payment_method'] = orders['payment_method'].astype(str).str.strip().str.upper()
    natural_key = [
        'customer_id', 'product_id', 'order_date', 'quantity', 
        'discount_pct', 'payment_method', 'rating', 'returned'
    ]
    orders = orders.drop_duplicates(subset=natural_key, keep='first')
    orders['discount_pct'] = orders['discount_pct'].fillna(0).astype(float)

    merged = orders.merge(products, on='product_id', how='left')
    merged['order_value'] = merged['quantity'] * merged['price'] * (1.0 - merged['discount_pct'] / 100.0)

    # 1. Visualization 1: Return Rate by Payment Method
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, ax = plt.subplots(figsize=(8, 5))

    payment_returns = (
        merged.groupby('payment_method')['returned']
        .mean()
        .mul(100)
        .round(1)
        .sort_values(ascending=False)
    )

    colors = ['#d9534f' if k == 'COD' else '#5bc0de' for k in payment_returns.index]
    bars = ax.bar(payment_returns.index, payment_returns.values, color=colors, width=0.55, edgecolor='black', linewidth=0.8)

    ax.set_title("COD Returns at 44.4% — 3x Card", fontsize=14, fontweight='bold', pad=15)
    ax.set_ylabel("Return Rate (%)", fontsize=11, fontweight='bold')
    ax.set_xlabel("Payment Method", fontsize=11, fontweight='bold')
    ax.set_ylim(0, 55)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.1f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5),
            textcoords="offset points",
            ha='center', va='bottom', fontsize=11, fontweight='bold'
        )

    plt.tight_layout()
    chart1_path = os.path.join(vis_dir, "return_rate_by_payment.png")
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"Saved: {chart1_path}")

    # 2. Visualization 2: Outlier-Corrected Monthly Revenue Trend
    # Detect outliers (Q3 + 1.5*IQR = 3.5)
    q1 = merged['quantity'].quantile(0.25)
    q3 = merged['quantity'].quantile(0.75)
    upper = q3 + 1.5 * (q3 - q1)
    cleaned_regular = merged[merged['quantity'] <= upper].copy()

    cleaned_regular['month'] = pd.to_datetime(cleaned_regular['order_date']).dt.to_period('M').astype(str)
    monthly_rev = cleaned_regular.groupby('month')['order_value'].sum()

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(monthly_rev.index, monthly_rev.values, marker='o', linewidth=2.5, color='#2e6da4', label='Corrected Net Revenue')

    # Highlight March peak
    march_val = monthly_rev['2026-03']
    ax.scatter(['2026-03'], [march_val], color='#d9534f', s=120, zorder=5, label='True Peak Month')
    ax.annotate(
        f"Peak: March (₹{march_val:,.2f})",
        xy=('2026-03', march_val),
        xytext=(-30, 18),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->", color='#d9534f', lw=1.5),
        fontsize=10, fontweight='bold', color='#d9534f'
    )

    ax.set_title("March 2026 is True Peak Month (Excluding B2B Wholesale Outliers)", fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Order Month (2026)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Revenue (INR)", fontsize=11, fontweight='bold')
    ax.set_ylim(8000, 23000)
    ax.legend(frameon=True)

    for x, y in zip(monthly_rev.index, monthly_rev.values):
        ax.annotate(f"₹{y:,.0f}", (x, y), textcoords="offset points", xytext=(0, -15), ha='center', fontsize=9)

    plt.tight_layout()
    chart2_path = os.path.join(vis_dir, "monthly_revenue_trend.png")
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"Saved: {chart2_path}")

if __name__ == "__main__":
    generate_visualizations()
