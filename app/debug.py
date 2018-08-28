from timeit import default_timer

class Debug():
    debugstrings = []
    starttime = ''
    counter = 0

    def add(self, item, max = 50):
        self.counter += 1
        if self.counter > max:
            return

        if type(item) == list:
            s = ' : '.join([str(s) for s in item])
        else:
            s = str(item)

        self.debugstrings.append(s)

    def timer(self, string = 'timer'):
        self.debugstrings.append(
            string + ': ' + str(default_timer() - self.starttime)
        )

    def resetcounter(self):
        self.counter = 0

    def __init__(self):
        self.debugstrings = []
        self.counter = 0
        self.starttime = default_timer()
        self.debugstrings.append('debug timer started')

    def __str__(self):
        s = r'\r\n'.join(self.debugstrings)
        return s

    @property
    def html(self) -> str:
        s = '<br />'.join(self.debugstrings)
        return s

    def print(self):
        s = '\r\n'.join(self.debugstrings)
        print(s)
