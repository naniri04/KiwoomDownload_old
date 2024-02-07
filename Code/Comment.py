''' # Get stock list
n = 0 # 0 = kospi, 10 = kosdaq
        outputStr = self.ocx.dynamicCall("GetCodeListByMarket(QString)", [f"{n}"])
        tempSplited = outputStr.split(';')
        db_control = sqlite3.connect("E:/StockDB/stock_master_list.db")
        db_executer = db_control.cursor()
        db_executer.execute("DROP TABLE Stock_master_list")
        db_executer.execute("CREATE TABLE Stock_master_list(StockCode text, StockName text)")
        
        for tempStr in tempSplited:
            stock_code = tempStr
            stock_name = self.ocx.dynamicCall("GetMasterCodeName(QString)", [stock_code])
            db_executer.execute(f"INSERT INTO Stock_master_list_kosdaq VALUES ('{stock_code}', '{stock_name}')")
            
        db_control.commit()
        db_control.close()
'''