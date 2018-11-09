# DB router for britpick_app

class BritpickAppDBRouter(object):
    """
    A router to control britpick_app db operations
    """
    def db_for_read(self, model, **hints):
        "Point all operations on britpick_app models to 'db_britpick_app'"
        from django.conf import settings
        if 'db_britpick_app' not in settings.DATABASES:
            return None
        if model._meta.app_label == 'britpick_app':
            return 'db_britpick_app'
        return None

    def db_for_write(self, model, **hints):
        "Point all operations on britpick_app models to 'db_britpick_app'"
        from django.conf import settings
        if 'db_britpick_app' not in settings.DATABASES:
            return None
        if model._meta.app_label == 'britpick_app':
            return 'db_britpick_app'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a model in britpick_app is involved"
        from django.conf import settings
        if 'db_britpick_app' not in settings.DATABASES:
            return None
        if obj1._meta.app_label == 'britpick_app' or obj2._meta.app_label == 'britpick_app':
            return True
        return None

    def allow_syncdb(self, db, model):
        "Make sure the britpick_app app only appears on the 'britpick_app' db"
        from django.conf import settings
        if 'db_britpick_app' not in settings.DATABASES:
            return None
        if db == 'db_britpick_app':
            return model._meta.app_label == 'britpick_app'
        elif model._meta.app_label == 'britpick_app':
            return False
        return None