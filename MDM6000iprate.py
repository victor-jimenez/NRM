"""
This script reads the current operating MODCOD, configured BW and calculates the available IP rate
"""

import time
import datetime
import threading
import configuration as cfg
import MDM6000 as newtec
import netbotDB

def pollandwrite(modem):
    DB = netbotDB.DB(mysqlIp, mysqlUser, mysqlPass)
    name = modem.getName()
    while True:
        try:
            modcod, efficiency, symbolrate = modem.snmpGetModcodSymbol()
        except:
            print("There was an error with the connection to the modem.")
            time.sleep(5)
            continue
        availableIPrate = symbolrate * float(efficiency)
        DB.resetOperationalSCPCflags(name)
        DB.insertOperationalSCPC(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), modem.getName(), str(modcod), str(efficiency), str(symbolrate), str(availableIPrate))
        time.sleep(5)

class aThread(threading.Thread):
    def __int__(self):
        threading.Thread.__init__(self)

if __name__ == '__main__':

    community = cfg.scpc['community']
    mysqlIp = cfg.mysql['host']
    mysqlUser = cfg.mysql['user']
    mysqlPass = cfg.mysql['password']

    DB = netbotDB.DB(mysqlIp, mysqlUser, mysqlPass)
    links = DB.getModemDetails()
    DB.close()
    modems = []
    for link in links:
        modems.append(newtec.modem(link[0], link[1], community))
    threads = []
    for modem in modems:
        threads.append(aThread(group=None, target=pollandwrite, name=None, args=(modem,)))
    for thread in threads:
        thread.start()
