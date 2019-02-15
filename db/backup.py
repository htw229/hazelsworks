import dbutils
import sys
import datetime



dbutils.createbackup(sys.argv[1])

day = datetime.datetime.now().day
if day == 1:
    dbutils.createbackup('monthly')
if day == 1 or day == 7 or day == 14 or day == 21 or day == 28:
    dbutils.createbackup('weekly')

dbutils.cleanbackupfolder()