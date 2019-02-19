import logging
import io
import re
import datetime

log_capture_string = io.StringIO()
# starttime = datetime.datetime.now()

msgpattern = r'(?P<datetime>\d.*) - (?P<module>.*) - (?P<messagetype>.*) - (?P<message>.*)'
datetimeformat = '%Y-%m-%d %H:%M:%S,%f'

class Logger(logging.Logger):
    def __init__(self, name):

        super().__init__(name)
        self.setLevel(logging.DEBUG)
        logger_handler = logging.StreamHandler(log_capture_string)
        logger_handler.setLevel(logging.DEBUG)
        logger_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.addHandler(logger_handler)



def loggeroutput():
    # global log_capture_string

    output = []
    modules = {}
    messagetypes = {}
    logs = []
    starttime = None

    log_contents = log_capture_string.getvalue().split('\n')
    for s in log_contents:
        match = re.match(msgpattern, s)
        if match:
            msgtime = datetime.datetime.strptime(match.group('datetime'), datetimeformat)
            if starttime is None:
                starttime = msgtime

            elapsedtime = msgtime - starttime
            elapsedseconds = round(elapsedtime.microseconds/1000000.0,1)
            elapsed = str(elapsedseconds).split('.')
            elapsedtime = elapsed[0].zfill(2) + '.' + elapsed[1]

            module = match.group('module')
            moduleclass = module.replace('.', '__')
            modules[module] = moduleclass

            messagetype = match.group('messagetype').lower()
            messagetypeclass = 'debug-level-%s' % messagetype
            messagetypes[messagetype] = messagetypeclass

            logs.append({
                'elapsedtime': elapsedtime,
                'module': module,
                'moduleclass': moduleclass,
                'messagetype': messagetype,
                'messagetypeclass': messagetypeclass,
                'message': match.group('message'),
            })



    # output.append('log contents')
    # output.append(log_contents)

    output = {
        'modules': modules,
        'messagetypes': messagetypes,
        'logs': logs,
    }

    log_capture_string.truncate(0)
    log_capture_string.seek(0)

    return output