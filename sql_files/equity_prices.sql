CREATE TABLE IF NOT EXISTS equity_prices (    "Date" date,
    "Open" float8,
    "High" float8,
    "Low" float8,
    "Close" float8,
    "Volume" int8,
    "Dividends" float8,
    "Stock Splits" float4,
    "ticker" varchar,
    PRIMARY KEY ("Date", "ticker")
);