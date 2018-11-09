from django.contrib import admin
from django import forms

from britpick_app.models import Suggestion, Dialect, Category, Explanation, Reference, Topic, Britpick, Search, SearchString, SearchGroup, SearchVariables, Word, WordGroup, Example, Spelling


class BaseAdmin(admin.ModelAdmin):
    exclude = ('date_created', 'date_edited',)

class DialectAdmin(admin.ModelAdmin):
    list_display = ('name', 'default', 'description')


class SearchForm(forms.ModelForm):
    class Meta:
        model = Search
        fields = '__all__'

    def clean(self):
        search_string = self.cleaned_data.get('search_string')
        search_group = self.cleaned_data.get('search_group')

        if search_string and search_group:
            raise forms.ValidationError('Cannot have both search string and search group')
        elif not search_string and not search_group:
            raise forms.ValidationError('Must have either search string or search group')

        return self.cleaned_data

class SearchAdmin(admin.ModelAdmin):
    form = SearchForm

admin.site.register(Search, SearchAdmin)





admin.site.register(Suggestion)

admin.site.register(Dialect, DialectAdmin)
admin.site.register(Category)
admin.site.register(Explanation)

admin.site.register(Reference)
admin.site.register(Topic)
admin.site.register(Britpick)

admin.site.register(SearchString)
admin.site.register(SearchGroup)
admin.site.register(SearchVariables)
admin.site.register(Word)
admin.site.register(WordGroup)
admin.site.register(Example)
admin.site.register(Spelling)