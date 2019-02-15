from subprocess import Popen
import datetime
import os
import re

BACKUP_PATH = "/home/htw/britpick/mysql_backups/"
DB = "htw$britpickdb"
MYSQLDUMP = "mysqldump -u htw -h htw.mysql.pythonanywhere-services.com '{database}'  > '{path}{filename}'"
MYSQLAPPLY = "mysql -u htw -h htw.mysql.pythonanywhere-services.com '{database}'  < '{path}{filename}'"

FILE_NAME = '{database}_{backup_type}_{timestamp}_{n}.sql'
FILE_NAME_PATTERN = r'(?P<db>.+?)_(?P<backup_type>.+?)_(?P<timestamp>.+?)\.sql'
FILE_NAME_SEARCH = '{database}_{backup_type}'



BACKUP_TYPES = {
    'daily':{
        'name': 'daily',
        'num_to_keep': 7,
    },
    'weekly':{
        'name': 'weekly',
        'num_to_keep': 4,
    },
    'monthly':{
        'name': 'monthly',
        'num_to_keep': 12,
    },
    'restore':{
        'name': 'monthly',
        'num_to_keep': 3,
    },
}

# DAILY_BACKUP = BACKUP_TYPES['daily']
# WEEKLY_BACKUP = BACKUP_TYPES['weekly']
# MONTHLY_BACKUP = BACKUP_TYPES['monthly']
# OTHER_BACKUP = BACKUP_TYPES['other']

# BACKUP_TYPES = [('daily', 2), ('weekly', 4), ('monthly', 12)]


def createbackup(backup_type_name = 'other'):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    filename = ''
    n = 0

    while True:
        filename = FILE_NAME.format(
            database=DB,
            backup_type=backup_type_name,
            timestamp=timestamp,
            n=str(n),
        )

        if filename not in os.listdir(BACKUP_PATH):
            break

        n += 1
        if n > 50:
            print("ERROR: infinite loop")
            return

    Popen(MYSQLDUMP.format(
        database=DB,
        path=BACKUP_PATH,
        filename=filename,
    ), shell=True)

    print('Backup saved to: %s' % filename)


def cleanbackupfolder():
    for _, backup_type in BACKUP_TYPES.items():
        backup_files = [f for f in os.listdir(BACKUP_PATH) if f.find(FILE_NAME_SEARCH.format(database=DB, backup_type=backup_type['name'],)) == 0]
        backup_files = sorted(backup_files, key=lambda f: os.path.getmtime(os.path.join(BACKUP_PATH, f)), reverse=True)

        files_to_delete = backup_files[backup_type['num_to_keep']:]

        for f in files_to_delete:
            os.remove(os.path.join(BACKUP_PATH, f))
            print('Removed: %s' % f)


def restorefrombackup(filename = None):
    BEFORE_RESTORE = 'before_restore'
    createbackup('before_restore')

    if filename is None:
        # apply last daily backup from specified database
        backup_files = [f for f in os.listdir(BACKUP_PATH) if f.find(FILE_NAME_SEARCH.format(database=DB, backup_type='daily',)) == 0]
        backup_files = sorted(backup_files, key=lambda f: os.path.getmtime(os.path.join(BACKUP_PATH, f)), reverse=True)
        filename = backup_files[1]

    print('Reverting from backup: %s' % filename)

    Popen(MYSQLAPPLY.format(
        database=DB,
        path=BACKUP_PATH,
        filename=filename,
    ), shell=True)

    # Popen("mysql -u htw -h htw.mysql.pythonanywhere-services.com 'htw$britpickdb'  < db-backup.sql", shell=True)