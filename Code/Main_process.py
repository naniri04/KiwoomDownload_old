import sys

sys.coinit_flags = 2
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QAxContainer import *
from PyQt5 import QtTest, QtCore
import pythoncom
import datetime
import sqlite3

import Auto_login, Code_Name, Debugging

currentPath = "C:\\Users\\naniri\\Code"

form_class = uic.loadUiType(currentPath + "\\untitled.ui")[0]

class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.is_logined = False
        self.is_received = False
        
        self.field_type_assign()
        
        self.is_next_exists = False
        self.searching_stock_name = ""
        self.searching_stock_code = ""
        
        self.db_control = any
        self.db_execute = any
        
        #for constant
        
        #for min_chart method
        self.prev_date = "_"
        self.TICK_RATE = "1"  # //
        
        #for continuous saving
        self.goal_cnt = 1
        self.done_cnt = 0
        
        self.event_assign()
        self.ocx.OnEventConnect.connect(self.connect_event)
        self.ocx.OnReceiveTrData.connect(self.tr_received_event)
        self.input_stock_code.installEventFilter(self)
        self.input_stock_code.setMaximumBlockCount(1)
        
    def time_YYMMDD(self) -> str:
        return datetime.datetime.now().strftime("%Y%m%d")
    def time_HHMMSS(self) -> str:
        return datetime.datetime.now().strftime("%H%M%S")
    
    def time_check(self) -> bool:
        if self.time_HHMMSS()[:2] == "04" and int(self.time_HHMMSS()[2:4]) > 30:
            return True
        else:
            return False
        
    # Button Event ---------------------
        
    def save_start_button_clicked(self):
        if self.save_combobox_1.currentIndex() == 0:  # 1개 조회
            self.goal_cnt = 1
            if self.save_combobox_2.currentIndex() == 0:    # DM
                self.day_call(stock_code=self.input_stock_code.toPlainText())
                QtTest.QTest.qWait(3700)
                self.min_call(stock_code=self.input_stock_code.toPlainText())
            elif self.save_combobox_2.currentIndex() == 1:  # D
                self.day_call(stock_code=self.input_stock_code.toPlainText())
            else:                                           # M
                self.min_call(stock_code=self.input_stock_code.toPlainText())
                
        else:                                         # 연속 조회
            text, ok = QInputDialog.getText(self, 'Input Value', 'Stock count:')
            if not ok:
                return
            
            self.goal_cnt = int(text)
            self.done_cnt = 0
            
            self.cont_saving(saving_type=self.save_combobox_2.currentIndex(), first_stock_info=self.input_stock_code.toPlainText())
            
    def login_button_clicked(self):
        self.ocx.dynamicCall("CommConnect()")
        self.status_label.setText('Connecting...')
        while not self.is_logined:
            pythoncom.PumpWaitingMessages()
        self.status_label.setText('Connected')
        self.login_button.setEnabled(False)
        self.test_button.setEnabled(True)
        is_save = False
        
        with open(currentPath + "\\time_reached.txt", "r") as f:
            if str.strip(f.readline()) == "1":
                is_save = True
                fsi = int(f.readline())
                self.done_cnt = int(f.readline())
                self.goal_cnt = int(f.readline())
                st = int(f.readline())
                
        if is_save:
            self.cont_saving(saving_type=st, first_stock_info=fsi)
                
        with open(currentPath + "\\time_reached.txt", "w") as f:
            f.write("0")
    
    def get_latest_clicked(self):
        with open(currentPath + "\\last_stock.txt", "r") as f:
            self.input_stock_code.setPlainText(f.read().strip())
            
    def prev_stock_button_clicked(self):
        if self.input_stock_code.toPlainText() == "000020":
            self.status_label.setText("Data Not Exists")
            return
        self.input_stock_code.setPlainText(Code_Name.get_prev(self.input_stock_code.toPlainText()))
        
    def next_stock_button_clicked(self):
        if self.input_stock_code.toPlainText() == "950220":
            self.status_label.setText("Data Not Exists")
            return
        self.input_stock_code.setPlainText(Code_Name.get_next(self.input_stock_code.toPlainText()))
        
    # Button Event End -----------------
    
    # Test -----------------------------
    
    def test_button_clicked(self):
        pass
    
    # Test End -------------------------
    
    # Database Making ------------------
    
    def eventFilter(self, obj, event) -> bool:
        if event.type() == QtCore.QEvent.KeyPress and obj is self.input_stock_code:
            if event.key() == QtCore.Qt.Key_Return and self.input_stock_code.hasFocus():
                tempStr = self.input_stock_code.toPlainText()
                self.input_stock_code.setPlainText(tempStr)
                if(not Code_Name.data_exist_check(tempStr)):
                    self.status_label.setText("Data Not Exists")
                    return super().eventFilter(obj, event)
                print(Code_Name.code_to_name(tempStr))
                self.status_label.setText("Data Found")
        return super().eventFilter(obj, event)
        
    def tr_received_event(self, screen_no, rq_name, tr_code, record_name, next_data_exists, uv1, uv2, uv3, uv4): # uv: unused val / next_data_exists -> 0: X, 2: O
        print("tr received")
        if next_data_exists == "2":
            self.is_next_exists = True
        elif next_data_exists == "0":
            self.is_next_exists = False
            
        if rq_name == "get_day_chart":
            self.day_chart(rq_name, tr_code, record_name)
            
        if rq_name == "get_min_chart":
            self.min_chart(rq_name, tr_code, record_name)
            
        self.is_received = True
            
    def cont_saving(self, saving_type:int, first_stock_info):
        code_tuple = Code_Name.get_code_list()
        first_stock_index = -1
        is_time_reached = False
        
        if type(first_stock_info) == str:
            first_stock_index = code_tuple.index(first_stock_info)
        elif type(first_stock_info) == int:
            first_stock_index = first_stock_info
        
        while True:
            if self.time_check():
                is_time_reached = True
                break
            
            if saving_type == 0:    # DM
                self.day_call(stock_code=code_tuple[first_stock_index + self.done_cnt])
                QtTest.QTest.qWait(3700)
                self.min_call(stock_code=code_tuple[first_stock_index + self.done_cnt])
            elif saving_type == 1:  # D
                self.day_call(stock_code=code_tuple[first_stock_index + self.done_cnt])
            elif saving_type == 2:  # M
                self.min_call(stock_code=code_tuple[first_stock_index + self.done_cnt])
            else:
                print("Error: saving type is not appropriate")
                return
            
            self.done_cnt += 1
            if self.done_cnt >= self.goal_cnt:
                self.status_label.setText('All Finished')
                break
            
        if is_time_reached:
            with open(currentPath + "\\time_reached.txt", "w") as f:
                f.write("1" + '\n')
                f.write(str(first_stock_index) + '\n')
                f.write(str(self.done_cnt) + '\n')
                f.write(str(self.goal_cnt) + '\n')
                f.write(str(saving_type))
                
            sys.exit(0)
    
    def call_data(self, opt_code:str, screen_no:str, rq_name:str, stock_code:str, id_list:tuple, val_list:tuple):   
        self._set_input_value(id_list=id_list, val_list=val_list)    
        self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)", rq_name, opt_code, 0, screen_no)
        self.status_label.setText('Operating...')
        self.searching_stock_code = stock_code
        self.searching_stock_name = Code_Name.code_to_name(stock_code)
        self.set_db_control()
        while True:
            if not self.is_received:
                pythoncom.PumpWaitingMessages()
            else:
                if self.is_next_exists:
                    self.status_label.setText(f'Waiting for Next [for {self.searching_stock_code}] [{self.done_cnt + 1}/{self.goal_cnt}]')
                    QtTest.QTest.qWait(3700)
                    self._set_input_value(id_list=id_list, val_list=val_list)
                    self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)", rq_name, opt_code, 2, screen_no)
                    self.status_label.setText('Operating...')
                    self.is_received = False
                    continue
                else:
                    self.is_received = False
                    break
        self.close_db_control()
        self.status_label.setText('Finished')
        
        with open(currentPath + "\\last_stock.txt", "w") as f:
            f.write(self.searching_stock_code)
            
    def set_db_control(self):
        self.db_control = sqlite3.connect(f"E://Stock/{self.searching_stock_code} {self.searching_stock_name}.db")
        self.db_executer = self.db_control.cursor()
        
    def close_db_control(self):
        self.db_control.commit()
        self.db_control.close()
    
    def _set_input_value(self, id_list:tuple, val_list:tuple):
        for i in range(len(id_list)):
            self.ocx.dynamicCall("SetInputValue(QString, QString)", id_list[i], val_list[i])
            
    def connect_event(self):
        self.is_logined = True
    
    def get_data(self, tr_code, record_name, idx, item_name):
        ret : str = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", tr_code, record_name, idx, item_name)
        return ret.strip()
    
    def day_chart(self, rq_name, tr_code, record_name):
        data_count = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", tr_code, rq_name)
        self.db_executer.execute("CREATE TABLE IF NOT EXISTS Day_chart(Date INTEGER, Open INTEGER, Highest INTEGER, Lowest INTEGER, Close INTEGER, Volume INTEGER)")
        
        for i in range(data_count):
            date = self.get_data(tr_code, record_name, i, "일자")
            open = self.get_data(tr_code, record_name, i, "시가")
            highest = self.get_data(tr_code, record_name, i, "고가")
            lowest = self.get_data(tr_code, record_name, i, "저가")
            close = self.get_data(tr_code, record_name, i, "현재가")
            volume = self.get_data(tr_code, record_name, i, "거래량")
            
            self.db_executer.execute(f"INSERT INTO Day_chart VALUES ({date}, {open}, {highest}, {lowest}, {close}, {volume})")
            
    def min_chart(self, rq_name, tr_code, record_name):
        data_count = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", tr_code, rq_name)
        self.db_executer.execute("CREATE TABLE IF NOT EXISTS Min_chart(Date INTEGER, Open INTEGER, Highest INTEGER, Lowest INTEGER, Close INTEGER, Volume INTEGER)")
        
        for i in range(data_count):
            data = []
            o_date = self.get_data(tr_code, record_name, i, "체결시간")
            data.append(self.get_data(tr_code, record_name, i, "시가"))
            data.append(self.get_data(tr_code, record_name, i, "고가"))
            data.append(self.get_data(tr_code, record_name, i, "저가"))
            data.append(self.get_data(tr_code, record_name, i, "현재가"))
            data.append(self.get_data(tr_code, record_name, i, "거래량"))
            
            m_date = ""
            if o_date[:8] != self.prev_date:
                self.prev_date = o_date[:8]
                m_date = o_date[:12]
            else:
                m_date = o_date[8:12]
            
            for i in range(5):
                if data[i][:1] == "-" or data[i][:1] == "+":
                    data[i] = data[i][1:]
            
            #self.prev_date = "asdf"
            self.db_executer.execute(f"INSERT INTO Min_chart VALUES ({m_date}, {data[0]}, {data[1]}, {data[2]}, {data[3]}, {data[4]})")

    def min_call(self, stock_code:str):
        self.call_data(opt_code="opt10080", screen_no="0101", rq_name="get_min_chart", stock_code=stock_code,
                                   id_list=("종목코드", "틱범위", "수정주가구분"), 
                                   val_list=(stock_code, self.TICK_RATE, "1"))
        
    def day_call(self, stock_code:str):
        self.call_data(opt_code="opt10081", screen_no="0101", rq_name="get_day_chart", stock_code=stock_code,
                                   id_list=("종목코드", "기준일자", "수정주가구분"), 
                                   val_list=(stock_code, self.time_YYMMDD(), "1"))
    
    # Database Making End --------------

    # Chart Project --------------------
            
    def y_hint_button_clicked(self):
        self.hint_window = AnotherWindow()
        self.hint_window.show()
            
    def y_simulate_button_clicked(self):
        pass
    
    # Chart Project End ----------------
    
    # UI Assign ------------------------
        
    def event_assign(self):
        self.login_button.clicked.connect(self.login_button_clicked)
        self.test_button.clicked.connect(self.test_button_clicked)
        self.save_start_button.clicked.connect(self.save_start_button_clicked)
        self.get_latest_stockcode.clicked.connect(self.get_latest_clicked)
        self.prev_stock_button.clicked.connect(self.prev_stock_button_clicked)
        self.next_stock_button.clicked.connect(self.next_stock_button_clicked)
        self.Y_hint_button.clicked.connect(self.y_hint_button_clicked)
        self.Y_simulate_button.clicked.connect(self.y_simulate_button_clicked)
                
    def field_type_assign(self):
        self.login_button : QPushButton
        self.status_label : QLabel
        self.test_button : QPushButton
        self.input_stock_code : QPlainTextEdit
        self.save_start_button : QPushButton
        self.save_combobox_1 : QComboBox
        self.save_combobox_2 : QComboBox
        self.get_latest_stockcode : QPushButton
        self.prev_stock_button : QPushButton
        self.next_stock_button : QPushButton
        self.Y_textEdit_1 : QTextEdit
        self.Y_textEdit_2 : QTextEdit
        self.Y_textEdit_3 : QTextEdit
        self.Y_textEdit_list = {'Peroid':self.Y_textEdit_1, 'Buy':self.Y_textEdit_2, 'Sell':self.Y_textEdit_3}
        self.Y_hint_button : QPushButton
        self.Y_simulate_button : QPushButton
        
    # UI Assign End --------------------
    
class AnotherWindow(QWidget):
    def __init__(self):
        # constant
        self.Y_HINT = "Italic = input. Bold = keyword<br><br>Peroid: <i>YYYYMMDD</i> <b>to</b> <i>YYYYMMDD</i><br>Condition: keyword: <b>and</b>, <b>or</b>, <b>()</b> /<br> <b>riseRate</b>, <b>accVolumeRate</b>, <b>accHighest</b>, <b>accLowest</b> /<br> inequality symbols, <b>=</b>, calc symbols /<br><b>medVolOf</b> <i>N</i>(days), <b>medPrcOf</b> <i>N</i>, <br><b>avgVolOf</b> <i>N</i>, <b>avgPrcOf</b> <i>N</i>"
        
        super().__init__()
        self.setFixedWidth(400)
        self.setFixedHeight(600)
        self.setWindowTitle("hint")
        
        layout = QVBoxLayout()
        self.hint_label = QLabel(text=self.Y_HINT)
        self.hint_label.setFixedSize(400, 600)
        self.hint_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        self.hint_label.setContentsMargins(5, 5, 5, 5)
        font = self.hint_label.font()
        font.setFamily('Roboto Slab Light')
        font.setPointSize(11)
        self.hint_label.setFont(font)
        
        layout.addWidget(self.hint_label)
        self.setLayout(layout)
    
if __name__ == "__main__":
    Auto_login.auto_login()
    Code_Name.sql_setting()
    
    app = QApplication(sys.argv)
    myWindow = MainWindow()
    
    myWindow.show()
    
    with open(currentPath + "\\is_auto_login.txt", "r") as f:
        if f.read() == "1":
            myWindow.login_button_clicked()
            
    sys.exit(app.exec_())