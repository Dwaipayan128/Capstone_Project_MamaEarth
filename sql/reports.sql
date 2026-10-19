-- Expected Output:
-- total_orders | total_revenue | avg_order_value
-- -------------+---------------+----------------
-- 180          | 99860.20      | 554.78
-- -----------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_orders,
    ROUND(SUM(o.quantity * p.price * (1.0 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_revenue,
    ROUND(AVG(o.quantity * p.price * (1.0 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS avg_order_value
FROM orders o
JOIN products p ON o.product_id = p.product_id;

-- Expected Output:
-- total_rows | rated_orders | unrated_orders
-- -----------+--------------+----------------
-- 180        | 165          | 15
-- -----------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_rows,
    COUNT(rating) AS rated_orders,
    COUNT(*) - COUNT(rating) AS unrated_orders
FROM orders;

-- Expected Output :
-- customer_id | name
-- ------------+-------
-- C045        | Vihaan
-- -----------------------------------------------------------------------------
-- Method 1: LEFT JOIN with HAVING
SELECT 
    c.customer_id, 
    c.name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) = 0;

-- Expected Output:
-- city      | total_orders | returned_orders | return_rate_pct
-- ----------+--------------+-----------------+----------------
-- Jaipur    | 19           | 8               | 42.1
-- Lucknow   | 49           | 15              | 30.6
-- Bangalore | 33           | 8               | 24.2
-- -----------------------------------------------------------------------------
SELECT 
    c.city,
    COUNT(o.order_id) AS total_orders,
    SUM(o.returned) AS returned_orders,
    ROUND((SUM(o.returned) * 100.0) / COUNT(o.order_id), 1) AS return_rate_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.city
HAVING return_rate_pct > 20.0
ORDER BY return_rate_pct DESC;

-- Expected Top 5 (LIMIT 5):
-- customer_id | name    | total_spend
-- ------------+---------+------------
-- C043        | Reyansh | 12920.00
-- C026        | Isha    | 8371.60
-- C008        | Meera   | 4564.60
-- C011        | Arjun   | 4111.00
-- C042        | Sanya   | 3785.00
--
-- Expected Sub-Slice Ranks 3-5 (LIMIT 3 OFFSET 2):
-- customer_id | name    | total_spend
-- ------------+---------+------------
-- C008        | Meera   | 4564.60
-- C011        | Arjun   | 4111.00
-- C042        | Sanya   | 3785.00
-- -----------------------------------------------------------------------------
-- Query 1: Top 5 spenders
SELECT 
    c.customer_id,
    c.name,
    PRINTF('%.2f', SUM(o.quantity * p.price * (1.0 - COALESCE(o.discount_pct, 0) / 100.0))) AS total_spend
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY SUM(o.quantity * p.price * (1.0 - COALESCE(o.discount_pct, 0) / 100.0)) DESC, c.customer_id ASC
LIMIT 5;

-- Query 2: Ranks 3 through 5 using OFFSET
SELECT 
    c.customer_id,
    c.name,
    PRINTF('%.2f', SUM(o.quantity * p.price * (1.0 - COALESCE(o.discount_pct, 0) / 100.0))) AS total_spend
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY SUM(o.quantity * p.price * (1.0 - COALESCE(o.discount_pct, 0) / 100.0)) DESC, c.customer_id ASC
LIMIT 3 OFFSET 2;


-- Expected Output:
-- category     | order_count | category_revenue
-- -------------+-------------+-----------------
-- Haircare     | 54          | 44956.10
-- Skincare     | 60          | 27346.00
-- Babycare     | 30          | 16805.00
-- PersonalCare | 36          | 10753.10
-- -----------------------------------------------------------------------------
SELECT 
    p.category,
    COUNT(o.order_id) AS order_count,
    ROUND(SUM(o.quantity * p.price * (1.0 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS category_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY p.category
ORDER BY category_revenue DESC;

-- Expected Output: 10 rows returned
-- (Aarav, Aditi, Ananya, Arjun, Aryan, Anika, Aditya, Aisha, Ayaan, Aria)
-- -----------------------------------------------------------------------------
SELECT 
    customer_id, 
    name, 
    city, 
    signup_date
FROM customers
WHERE name LIKE 'A%';

-- Expected Output: exactly 4 rows
-- acquisition_source
-- ------------------
-- Ad
-- Organic
-- Referral
-- Social
-- -----------------------------------------------------------------------------
SELECT DISTINCT 
    acquisition_source
FROM customers
ORDER BY acquisition_source ASC;


-- Expected Output:
-- loyalty_tier | COUNT(*)
-- -------------+---------
-- Gold         | 28
-- Silver       | 17
-- -----------------------------------------------------------------------------
ALTER TABLE customers ADD COLUMN loyalty_tier VARCHAR(10);

UPDATE customers 
SET loyalty_tier = CASE 
    WHEN city_tier = 1 THEN 'Gold' 
    ELSE 'Silver' 
END;

-- Verification:
SELECT 
    loyalty_tier, 
    COUNT(*) AS customer_count
FROM customers
GROUP BY loyalty_tier
ORDER BY loyalty_tier ASC;
