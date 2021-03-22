
""" Here we save the sql table templates.
    Other functions can call it for creating new table.

    NOTE: The first column would be set as key column.
"""

SYMBOLS_DETAILS = {
    "symbol": "CHAR(20)",
    "shortName": "TEXT",
    "longName": "TEXT",
    "sector": "CHAR(100)",
    "industry": "CHAR(100)",
    "sharesOutstanding": "BIGINT",
    "marketCap": "BIGINT",
    "finCurrency": "CHAR(10)"
}