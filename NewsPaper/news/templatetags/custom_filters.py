from django import template
import os

register = template.Library()


bad_words = [
    'bad_wi', 'xxx', 'aqw', 'очень', 'bfd', 'bad', 'плохое',
    'слово', 'arse', 'dolby', 'классический', 'cтатистика',
]


@register.filter(name='censor')
def censor(value):
    # module_dir = os.path.dirname(__file__)
    # file_path = os.path.join(module_dir, 'censor_list.txt').encode('utf-8')
    # bad_words = open(file_path, 'r').read()

    x = value.lower()
    if ' ' in x:
        a = list(x.split(' '))
        for i in a:
            if i in bad_words:
                y = a.index(i)
                a.remove(i)
                a.insert(y, '@!%&!2')
                value = (" ".join(a))
                return value

    if x in bad_words:
        x = '@!%&!'
        return x
    else:
        return x


# ===============================================================================
# @register.filter(name='censor')
# def censor(value):
#     censored, default = '', value.split()
#     file = open('news/templatetags/censor_list.txt', 'r', encoding='utf8')
#     text = file.read().split(', ')
#     file.close()
#     for word in default:
#         for cen in text:
#             if cen in word:
#                 word = word[0] + '*' * (len(word) - 1)
#         censored += word + ' '
#     return censored


#  ==============================================================================
# @register.simple_tag(takes_context=True)
# def param_replace(context, **kwargs):
#
#     d = context['request'].GET.copy()
#     for k, v in kwargs.items():
#         d[k] = v
#     for k in [k for k, v in d.items() if not v]:
#         del d[k]
#     return d.urlencode()
