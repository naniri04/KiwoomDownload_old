import sqlite3
import datetime
#import Main_process
import os
import math
import matplotlib.pyplot as plt
import matplotlib.style as matstyle
import numpy

if __name__ == "__main__":
    matstyle.use('fast')
        
    folderPath = "C:/Users/naniri/StockDBMed/Stock"
    
    fileNameList = os.listdir(folderPath)
    
    for i in range(len(fileNameList)): #len(fileNameList)
        db_control = sqlite3.connect(folderPath + "/" + fileNameList[i]) #fileNameList[i]
        db_executer = db_control.cursor()
        
        firstRowid = 1
        noData = False
        while True:
            if firstRowid > 15:
                noData = True
                break
            
            db_executer.execute(f"select rowid from Day_chart where rowid = {firstRowid}")
            if db_executer.fetchone() == None:
                firstRowid += 1
                continue
            else:
                break
            
        if noData:
            print(f"no data in {fileNameList[i]}")
            continue
        
        db_executer.execute("select Volume from Day_chart")
        temp1 = db_executer.fetchall()
        VolumeList = [data[0] for data in temp1]
        
        for count in range(len(VolumeList) - 31):
            db_executer.execute(f"update Day_chart set VolMed = {numpy.median(VolumeList[count + 1 : count + 32])} where rowid = {firstRowid + count}")
        
        db_control.commit()
        db_control.close()            
        