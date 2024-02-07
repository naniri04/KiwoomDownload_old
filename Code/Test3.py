import sqlite3
import datetime
#import Main_process
import os
import math
import matplotlib.pyplot as plt
import matplotlib.style as matstyle
import numpy

if __name__ == "__main__":
            
    folderPath = "C:/Users/naniri/StockDBMed/Stock"
    
    fileNameList = os.listdir(folderPath)
    
    for i in range(len(fileNameList)): #len(fileNameList)
        db_control = sqlite3.connect(folderPath + "/" + fileNameList[i]) #fileNameList[i]
        db_executer = db_control.cursor()
        
        db_executer.execute("delete from Day_chart where VolMed is null")
        
        db_control.commit()
        db_control.close()
            
        