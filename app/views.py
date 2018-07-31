import django.shortcuts


def robotstxt(request):
    """
    This will serve the robots.txt file located in the static folder.

    :param request:
    :return:
    """
    return django.shortcuts.render(request, 'robots.txt')