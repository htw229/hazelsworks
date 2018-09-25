from timeit import default_timer
import html

class Debug:
    debugstrings = []
    starttime = ''
    counter = 0
    paused = False
    max_reached_message = False
    timers = {}

    def add(self, item, *args, max = 500):
        if self.paused:
            return

        self.counter += 1
        if self.counter > max:
            # indicate that have reached max in counter
            if not self.max_reached_message:
                self.debugstrings.append('...')
                self.max_reached_message = True
            return

        strings = []

        if type(item) == list:
            strings.extend(item)
        else:
            strings.append(item)

        strings.extend(args)

        s = ' : '.join([str(s) for s in strings])

        self.debugstrings.append(s)

    def timer(self, string = 'timer'):
        self.debugstrings.append(
            string + ': ' + str(default_timer() - self.starttime)
        )

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
        self.starttime = default_timer()
        self.debugstrings.append('debug timer started')

    def __str__(self):
        s = r'  |  '.join(self.debugstrings)
        return s

    @property
    def html(self) -> str:
        s = '<br />'.join([html.escape(s) for s in self.debugstrings])
        return s

    def print(self):
        s = '\r\n'.join(self.debugstrings)
        print(s)
