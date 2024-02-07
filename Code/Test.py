import sqlite3
import datetime
import Main_process
import os
import math
import matplotlib.pyplot as plt
import matplotlib.style as matstyle
import matplotlib.ticker as ticker
import mplfinance as mplfi
from mplfinance.original_flavor import candlestick2_ohlc
import numpy
import pandas

if __name__ == "__main__":
    matstyle.use('fast')
    
    folderPath = "C:/Users/naniri/StockDB/Stock"
    
    fileNameList = os.listdir(folderPath)
    
    fig, ax = plt.subplots()
    for i in range(13, 14): #len(fileNameList)
        db_control = sqlite3.connect(folderPath + "/" + fileNameList[i]) #fileNameList[i]
        db_executer = db_control.cursor()
        
        tempList = db_executer.execute("select rowid, Date from Day_chart where Rate > 28 and Date > 20211201").fetchall() # and Date > 20211201
        targList = []
        prevList = []
        tempList2 = []
        for tempVal in tempList:
            tempList2.append(tempVal[0]+1)
            targList.append(tempVal[1])
        tempList.clear()
        tempList = db_executer.execute(f"select Close from Day_chart where rowid in ({str(tempList2)[1:-1]})").fetchall()
        for j in tempList:
            prevList.append(j[0])
        
        for l in range(1): #len(targList)
            targDate = targList[l]
            db_executer.execute(f"select rowid from Min_chart where Date/10000 == {targDate}")
            start_rowid = db_executer.fetchone()[0]
            db_executer.execute(f"select rowid from Min_chart where Date > 10000 and Date/10000 < {targDate} limit 1")
            end_rowid = db_executer.fetchone()[0]
            
            db_executer.execute(f"select Date, Close from Min_chart where rowid > {start_rowid} and rowid < {end_rowid}")
            raw_data_list = db_executer.fetchall()
            raw_data_list.reverse()
            
            sorted_data_list = {'Time':[], 'CloseRate':[]}
            
            
            for k in raw_data_list:
                sorted_data_list['Time'].append(str(k[0]))
                sorted_data_list['CloseRate'].append((k[1] - prevList[l]) / prevList[l])
            
            df = pandas.DataFrame(sorted_data_list)
            print(df)
            ax.plot(df.Time, df.CloseRate, alpha=0.2, linewidth=1)
    
    ax.xaxis.set_major_locator(ticker.MaxNLocator(17))
    plt.xticks(rotation = 45, fontsize=7)
    #ax.legend(loc=1)
    plt.show()
    
    #db_control.commit()
    db_control.close()
    '''df = pandas.DataFrame.from_records(data=wholeInfoTuple, columns=['Date', 'Open', 'Highest', 'Lowest', 'Close'])
    df = df.astype({'Date':'str'})'''
        