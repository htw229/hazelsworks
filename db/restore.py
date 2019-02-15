import dbutils
import sys

try:
    dbutils.restorefrombackup(filename = sys.argv[1])
except IndexError:
    dbutils.restorefrombackup()