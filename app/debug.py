from timeit import default_timer
import html

class Debug:
    debugstrings = []
    inittime = ''
    previoustime = ''
    counter = 0
    paused = False
    max_reached_message = False
    timers = {}
    addloops = {}

    def add(self, *args, max = 500, loop='', showloopname=False, sectionbreakbefore=False, sectionbreakafter=False, blanklineafter=True):
        if self.paused:
            return

        if loop:
            if loop not in self.addloops.keys():
                self.addloops[loop] = {
                    'max': max,
                    'i': 1,
                }
            elif self.addloops[loop]['i'] == self.addloops[loop]['max']:
                self.debugstrings.append('...')
                self.blankline()
                self.addloops[loop]['i'] += 1
                return
            elif self.addloops[loop]['i'] > self.addloops[loop]['max']:
                return
            else:
                self.addloops[loop]['i'] += 1
        else:
            self.counter += 1
            if self.counter > max:
                # indicate that have reached max in counter
                if not self.max_reached_message:
                    self.debugstrings.append('...')
                    self.max_reached_message = True
                return

        strings = []

        if loop and showloopname:
            strings.append(loop)

        for item in args:
            if type(item) == list:
                strings.extend(item)
            else:
                strings.append(item)

        s = ' : '.join([str(s) for s in strings])

        if sectionbreakbefore:
            self.sectionbreak()

        self.debugstrings.append(s)

        if sectionbreakafter:
            self.sectionbreak()
        elif blanklineafter:
            self.blankline()

    def sectionbreak(self, *args, char=r' * '):
        breaklength = 30
        if args:
            self.blankline()
            self.debugstrings.append(char * breaklength)
            self.add(*args, blanklineafter=False)
            self.debugstrings.append(char * breaklength)
            self.blankline()
        else:
            self.blankline()
            self.debugstrings.append(char * breaklength)
            self.blankline()

    def blankline(self, lines=1):
        for _ in range(lines):
            self.debugstrings.append(' ')

    def timer(self, string = 'timer', useinittime = False):
        if useinittime:
            starttime = self.inittime
        else:
            starttime = self.previoustime

        elapsed = round(default_timer() - starttime, 2)
        self.add('--< ' + string, elapsed)
        self.previoustime = default_timer()

    def timerstart(self, timername):
        self.timers[str(timername)] = default_timer()

    def timerend(self, timername):
        self.debugstrings.append(
            'TIMER: ' + str(timername) + ': ' + str(default_timer() - self.timers[str(timername)])
        )


    def resetcounter(self):
        self.counter = 0

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False

    def __init__(self):
        self.debugstrings = []
        self.counter = 0
        self.inittime = default_timer()
        self.previoustime = self.inittime
        # self.debugstrings.append('debug timer started')

    def __str__(self):
        s = r'  |  '.join(self.debugstrings)
        return s

    @property
    def html(self) -> str:
        self.timer('total time', useinittime=True)
        s = '<br />'.join([html.escape(s) for s in self.debugstrings])
        return s

    def print(self):
        s = '\r\n'.join(self.debugstrings)
        print(s)
