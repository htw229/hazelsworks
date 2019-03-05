import logging
import io
import re
import datetime

log_capture_string = io.StringIO()
# starttime = datetime.datetime.now()

# formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s %(tags)s'

msgpattern = r'(?P<datetime>\d.*) - (?P<module>.*) - (?P<messagetype>.*) - (?P<message>.*) \[(?P<tags>.*)\]'
tagpattern = r"(?<=')([^']+)(?:'(?:, '|))"
datetimeformat = '%Y-%m-%d %H:%M:%S,%f'

class Logger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)
        self.setLevel(logging.DEBUG)
        logger_handler = logging.StreamHandler(log_capture_string)
        logger_handler.setLevel(logging.DEBUG)
        logger_handler.setFormatter(logging.Formatter(formatter))
        self.addHandler(logger_handler)

    def _log(self, *args, tags = None, **kwargs):
        if tags is None:
            tags = []

        kwargs['extra'] = {'tags': tags}
        super()._log(*args, **kwargs)


def loggeroutput():
    # global log_capture_string

    output = []
    modules = {}
    messagetypes = {}
    tags = {}
    logs = []

    starttime = None

    log_contents = log_capture_string.getvalue().split('\n')
    for s in log_contents:
        match = re.match(msgpattern, s)
        if match:
            logclasses = []

            logtime = match.group('datetime')
            msgtime = datetime.datetime.strptime(logtime, datetimeformat)
            if starttime is None:
                starttime = msgtime

            elapsedtime = msgtime - starttime
            elapsedseconds = round(elapsedtime.microseconds/1000000.0,1)
            elapsed = str(elapsedseconds).split('.')
            elapsedtime = elapsed[0].zfill(2) + '.' + elapsed[1]

            module = match.group('module')
            moduleclass = module.replace('.', '__')
            modules[module] = moduleclass
            logclasses.append(moduleclass)

            messagetype = match.group('messagetype').lower()
            messagetypeclass = 'debug-level-%s' % messagetype
            messagetypes[messagetype] = messagetypeclass
            logclasses.append(messagetypeclass)

            message = match.group('message')

            msgtags = re.findall(tagpattern, match.group('tags'))
            tagstring = ' '.join('#' + s for s in msgtags)
            tagclasses = ['debugtag-' + t for t in msgtags]
            for t in msgtags:
                tags[t] = 'debugtag-%s' % t
            logclasses.extend(tagclasses)

            logs.append({
                'logtime': logtime,
                'elapsedtime': elapsedtime,
                'module': module,
                'moduleclass': moduleclass,
                'messagetype': messagetype,
                'messagetypeclass': messagetypeclass,
                'message': message,
                'tags': tagstring,
                'tagclasses': tagclasses,
                'classes': logclasses,
            })

    logitemdisplay = [
        {'name': 'logtime', 'visible': False},
        {'name': 'elapsedtime', 'visible': True},
        {'name': 'module', 'visible': False},
        {'name': 'messagetype', 'visible': False},
        {'name': 'message', 'visible': True},
        {'name': 'tags', 'visible': True},
    ]

    logitemclasses = {}

    for logitem in logitemdisplay:
        logitemname = logitem['name']
        logitemclasses[logitemname] = 'logitem-' + logitemname

    output = {
        'modules': modules,
        'messagetypes': messagetypes,
        'logitemclasses': logitemclasses,
        'logitemdisplay': logitemdisplay,
        'tags': tags,
        'logs': logs,
    }

    log_capture_string.truncate(0)
    log_capture_string.seek(0)

    return output