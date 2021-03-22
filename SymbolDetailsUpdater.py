
from . import mysql
from . import timestamp
from . import TerminalReporter
from . import yfapi
from . import SQLTemples

import os
import json


class Updater:

    def __init__(self, sql_config_path: str = None):
        if sql_config_path == None:
            self.sql_config_path = "./sql_config.json"
        else:
            self.sql_config_path = sql_config_path
        self.__get_sql_config()
        self.symbolDB = mysql.DB("symbols", self.host,
                                 self.port, self.user, self.password)
        self.__save_sql_config()
        self.__initialize_DB()
        self.symbolsTB = self.symbolDB.TB("symbols")
        self.symbolDetailsTB = self.symbolDB.TB("symbol_details")
    
    def update_US(self):
        """
        Update symbol details of US market.
        """
        reporter = TerminalReporter.Reporter("SymbolDeatilsUpdater", "Updating US symbols...")
        reporter.report()
        symbols = self.symbolsTB.query("*", "WHERE market = 'us' AND enable = true")
        symbols_updates = {}
        symbolDetails_updates = {}
        reporter.what = "Updating symbol details..."
        reporter.initialize_stepIntro(len(symbols))
        for symbol in symbols:
            reporter.report(True)
            query = yfapi.YFAPI(symbol)
            symbols_updates[symbol] = {"type": query.quoteType()}
            symbolDetails_updates[symbol] = {
                "shortName": query.shortName(),
                "longName": query.longName(),
                "sector": query.sector(),
                "industry": query.industry(),
                "sharesOutstanding": query.sharesOutstanding(),
                "marketCap": query.marketCap(),
                "finCurrency": query.financialCurrency()
            }
        # update to sql server
        reporter.what = "Updating SQL Server..."
        reporter.report()
        if len(symbols_updates) > 0:
            self.symbolsTB.update(symbols_updates)
        if len(symbolDetails_updates) > 0:
            self.symbolDetailsTB.update(symbolDetails_updates)
        self.symbolDB.commit()
        self.symbolDB.close()
        reporter.what = "Done."
        reporter.report()


    def __initialize_DB(self):
        tbs = self.symbolDB.list_tb()
        if not "symbol_details" in tbs:
            self.__create_tb_with_templates(
                "symbol_details", SQLTemples.SYMBOLS_DETAILS)

    def __create_tb_with_templates(self, tableName: str, temp: dict):
        colnames = list(temp.keys())
        # first column as key column
        tb = self.symbolDB.add_tb(tableName, colnames[0], temp[colnames[0]])
        for i in range(1, len(colnames)):
            colname = colnames[i]
            tb.add_col(colname, temp[colname])

    def __get_sql_config(self):
        if not os.path.exists(self.sql_config_path):
            with open(self.sql_config_path, 'w') as f:
                j = {"host": "", "port": 0, "user": "", "password": ""}
                f.write(json.dumps(j))
        with open(self.sql_config_path, 'r') as f:
            sql_config = json.loads(f.read())
        self.host = sql_config["host"]
        self.port = sql_config["port"]
        self.user = sql_config["user"]
        self.password = sql_config["password"]

    def __save_sql_config(self):
        j = self.symbolDB.get_loginInfo()
        with open(self.sql_config_path, 'w') as f:
            f.write(json.dumps(j))
