"""
This script reads the current operating MODCOD, configured BW and calculates the available IP rate
"""

from pysnmp.hlapi import *
import csv
import time
import datetime
import mysql.connector
import threading

class newtecModem(object):

    def __init__(self, name, ip, community):
        self.name = name
        self.ip = ip
        self.community = community
        self.modcodOID = '1.3.6.1.4.1.5835.5.2.2100.1.2.1.1.4.1'
        self.symbolrateOID = '1.3.6.1.4.1.5835.5.2.2100.1.1.3.0'
        self.efficiencyTable = self.loadEfficiencyTable()

    def getName(self):
        return self.name

    def getIP(self):
        return  self.ip

    def getCommunity(self):
        return self.community

    def loadEfficiencyTable(self):
        csvReader = csv.reader(open(
            'C:\\Users\Victor_Jimenez\PycharmProjects\The Python Megacourse\Work Projects\SCPC modems\efficiency_table.csv'))
        efficiencyTable = {}
        for row in csvReader:
            key = row[1]
            efficiencyTable[key] = [row[0], row[2]]
        return efficiencyTable

    def snmpget(self):

        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
            CommunityData(self.community, mpModel=0),
            UdpTransportTarget((self.ip, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(self.modcodOID)),
            ObjectType(ObjectIdentity(self.symbolrateOID)),
            lookupMib=False)
            )

        if errorIndication:
            print(errorIndication)
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            return(self.efficiencyTable.get(str(varBinds[0][1]))[0], self.efficiencyTable.get(str(varBinds[0][1]))[1], varBinds[1][1])

class netbotDB(object):

    def __init__(self, ip, user, password):
        self.ip = ip
        self.user = user
        self.password = password
        self.connection = self.connect()

    def connect(self):
        try:
            return mysql.connector.connect(user=self.user, password=self.password, host=self.ip)
        except:
            print("There was an error connecting to the DB.")
            return

    def close(self):
        self.connection.close()
        return

    def query(self, sql):
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
        except:
            self.connection = self.connect()
            cursor = self.connection.cursor()
            cursor.execute(sql)
        try:
            return cursor.fetchall()
        except:
            self.connection.commit()
            return

    def resetOperationalSCPCflags(self, name):
        sql = "update WAN.operationalSCPC set latest = 0 where latest = 1 and link = \"" + name + "\";"
        self.query(sql)
        return

    def insertOperationalSCPC(self, date, link, modcod, efficiency, symbolrate, availableIPrate):
        sql = "insert into WAN.operationalSCPC values (\""+ date + "\", \"" + link + "\", \"" + modcod + "\", " + efficiency + ", " + symbolrate + ", " + availableIPrate + ", 1);"
        self.query(sql)
        return

    def getModemDetails(self):
        sql = "select distinct link, IP from configuration.remote;"
        return self.query(sql)

def pollandwrite(modem):
    DB = netbotDB(mysqlIp, mysqlUser, mysqlPass)
    name = modem.getName()
    while True:
        try:
            modcod, efficiency, symbolrate = modem.snmpget()
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

    community = 'icghol'
    mysqlIp = "10.214.12.35"
    mysqlUser = "netbot"
    mysqlPass = "mtn33025!"

    DB = netbotDB(mysqlIp, mysqlUser, mysqlPass)
    links = DB.getModemDetails()
    DB.close()
    modems = []
    for link in links:
        modems.append(newtecModem(link[0], link[1], community))
    threads = []
    for modem in modems:
        threads.append(aThread(group=None, target=pollandwrite, name=None, args=(modem,)))
    for thread in threads:
        thread.start()