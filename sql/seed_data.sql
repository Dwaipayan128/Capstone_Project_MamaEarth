UPDATE orders1
SET discount_pct = NULL 
WHERE discount_pct = '' OR discount_pct IS NULL;

UPDATE orders1
SET rating = NULL 
WHERE rating = '' OR rating IS NULL;

SELECT COUNT(*) FROM customers1;
SELECT COUNT(*) FROM products1;
SELECT COUNT(*) FROM orders1;
