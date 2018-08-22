from timeit import default_timer

class Debug():
    debugstrings = []
    starttime = ''

    def add(self, item):
        if type(item) == list:
            s = ' : '.join(item)
        else:
            s = str(item)

        self.debugstrings.append(s)

    def timer(self, string = 'timer'):
        self.debugstrings.append(
            string + ': ' + str(default_timer() - self.starttime)
        )

    def __init__(self):
        self.starttime = default_timer()
        self.debugstrings.append('debug timer started')

    def __str__(self):
        s = r'\r\n'.join(self.debugstrings)
        return s

    @property
    def html(self) -> str:
        s = '<br />'.join(self.debugstrings)
        return s