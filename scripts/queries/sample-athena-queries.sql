-- Register all partitions first (run once)
MSCK REPAIR TABLE stock_prices;

-- Query using partition keys (fastest + cheapest)
SELECT * FROM stock_prices
WHERE symbol = 'TSLA'
AND date = '2026-03-10'
AND hour = 14;

-- Average closing price per day per stock
SELECT symbol, date, ROUND(AVG(close), 2) AS avg_close
FROM stock_prices
GROUP BY symbol, date
ORDER BY date DESC;

-- Highest price NVDA ever hit
SELECT symbol, event_time, high
FROM stock_prices
WHERE symbol = 'NVDA'
ORDER BY high DESC
LIMIT 5;

-- Trading volume by hour
SELECT hour, SUM(volume) AS total_volume
FROM stock_prices
GROUP BY hour
ORDER BY total_volume DESC;
