from msilib.schema import AppId
from prompt_toolkit import Application
from pywinauto import application
from pywinauto import timings
import time
import os

def auto_login():
    opversionup = application.Application(backend = "uia").start("C:\OpenAPI\opversionup.exe")
    dlg_spec: application.WindowSpecification
    
    while(True):
        time.sleep(0.5)
        dlg_spec = opversionup.window(title='업그레이드 확인')
        if (dlg_spec.exists() or dlg_spec.child_window(title="확  인", auto_id="1", control_type="Button").exists()):
            break
        else: continue
        
    dlg_spec.child_window(title="확  인", auto_id="1", control_type="Button").click()
    #dlg_spec.print_control_identifiers()
    
    #for i in range(3):
    #    print(f"waiting...{i}")
    #    time.sleep(1)
    
#auto_login()