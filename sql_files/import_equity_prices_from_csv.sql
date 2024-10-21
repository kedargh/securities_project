
CREATE OR REPLACE FUNCTION import_equity_prices_from_csv()
RETURNS void AS $$
BEGIN
    COPY EQUITY_PRICES (date, open, high, low, close, volume, ticker)
    FROM '/storage/v1/object/public/equity_data_bucket/equity_data.csv' 
    WITH (FORMAT csv, HEADER true);
END;
$$ LANGUAGE plpgsql;
