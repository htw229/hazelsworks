from django.contrib import admin

# Register your models here.
from .models import BritpickDialects
admin.site.register(BritpickDialects)

from .models import ReplacementExplanation
admin.site.register(ReplacementExplanation)

from .models import BritpickFindReplace
admin.site.register(BritpickFindReplace)