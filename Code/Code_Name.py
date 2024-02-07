import sqlite3
import types

def code_to_name(code:str) -> str:
    db_executer.execute(f"SELECT StockName FROM Stock_list WHERE StockCode = '{code}'")
    return db_executer.fetchone()[0]

def name_to_code(name:str) -> str:
    db_executer.execute(f"SELECT StockCode FROM Stock_list WHERE StockName = '{name}'")
    return db_executer.fetchone()[0]

def sql_setting():
    global db_control, db_executer
    db_control = sqlite3.connect("C:/Users/naniri/StockDB/stock_list.db")
    db_executer = db_control.cursor()
    
def get_prev(code:str) -> str:
    db_executer.execute(f"SELECT ID FROM Stock_list WHERE StockCode = '{code}'")
    id = int(db_executer.fetchone()[0])
    db_executer.execute(f"SELECT StockCode FROM Stock_list WHERE ID = {id-1}")
    return db_executer.fetchone()[0] 
    
def get_next(code:str) -> str:
    db_executer.execute(f"SELECT ID FROM Stock_list WHERE StockCode = '{code}'")
    id = int(db_executer.fetchone()[0])
    db_executer.execute(f"SELECT StockCode FROM Stock_list WHERE ID = {id+1}")
    return db_executer.fetchone()[0]  

def data_exist_check(code:str) -> bool:
    db_executer.execute(f"SELECT ID FROM Stock_list WHERE StockCode = '{code}'") 
    if(db_executer.fetchone() is None):
        return False
    else:
        return True

def get_code_list() -> tuple:
    ret = []
    db_executer.execute("SELECT StockCode FROM Stock_list")
    for _ in range(2434):
        ret.append(db_executer.fetchone()[0].strip())
    return tuple(ret)

def close():
    db_control.close()