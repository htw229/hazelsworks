from django.db import models

class BritpickDialects(models.Model):
    name = models.CharField(max_length=100, db_index=True)

class BritpickFindReplace(models.Model):
    dialect = models.ForeignKey(BritpickDialects, blank=True, null=True, db_index=True, on_delete="cascade")
    searchwords = models.TextField(blank=True, null=True)
    directreplacement = models.CharField(blank=True, null=True, max_length=200)
    considerreplacement = models.TextField(blank=True, null=True)
    clarifyreplacement = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)




