"""
This script reads the current modem encapsulation configuration and parses it to get traffic classes detailed information
"""

from pysnmp.hlapi import *
import csv
import time
import datetime
import mysql.connector
import threading
import operationalSCPCconfig as cfg