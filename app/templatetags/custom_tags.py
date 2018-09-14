from django import template
from django.template.loader import get_template
from django.template import Context, Template

register = template.Library()


# get whole text string such as
# <p>hello {{ inputword }} {{ replacement }}</p>
# and output html

@register.simple_tag(name='outputtexttemplate')
def outputtexttemplate(outputtext, replacements):

    # t = get_template('inline_replacement.html')
    # t = Template('{{ testtag }}')

    # t = Template(outputtext)

    #TODO: need to pass along dict of replacement
    # parse input text to get included inline_replacement.html as new template string (with string x and replacement obj number as parameters
    # parse results of that to get final html

    # d = {'inputtext': replacements[56]}
    # c = Context(d)
    # s = t.render(c)

    t = Template(outputtext)
    d = {'replacements': replacements}
    c = Context(d)
    s = t.render(c)

    return s

# @register.inclusion_tag('inline_replacement.html')
# def any_function():
#   variable = YourModel.objects.order_by('-publish')[:5]
#   return {'variable': variable}

# @register.inclusion_tag('inline_replacement.html', takes_context=True)
# def show_text(context):
#     return 'hello'

