from .models import BritpickDialects, BritpickFindReplace
from .debug import Debug as DebugClass

debug = DebugClass()

def changebritishdialectname():
    for obj in BritpickFindReplace.objects.all():
        if obj.dialect.name == 'British (Generic)':
            obj.dialect = BritpickDialects.objects.get(name='British')
            obj.save()
            debug.add(['obj', obj], max=10)
    debug.print()
