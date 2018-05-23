"""
Support functions to interact with netbot database
"""

import mysql.connector


class DB(object):

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