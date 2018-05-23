"""
Support functions to interact with Newtec MDM6000 modem
"""

from pysnmp.hlapi import *
import csv

class modem(object):

    def __init__(self, name, ip, community=icghol):
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
            './efficiency_table.csv'))
        efficiencyTable = {}
        for row in csvReader:
            key = row[1]
            efficiencyTable[key] = [row[0], row[2]]
        return efficiencyTable

    def snmpGetModcodSymbol(self):

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