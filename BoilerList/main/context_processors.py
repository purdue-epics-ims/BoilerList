from django.conf import settings

def global_settings(request):
    return { 'SETTINGS': settings }
