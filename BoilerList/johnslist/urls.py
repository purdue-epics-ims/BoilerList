from django.conf.urls import include, url
from django.contrib import admin
from johnslist import settings
from main import urls
from django.views.static import serve
# import notifications
# url('^inbox/notifications/', include(notifications.urls)),

urlpatterns = [
    url(r'^password_reset/', include('password_reset.urls')),
	url(r'^admin/', include(admin.site.urls),name='admin'),
	url(r'^', include(urls),name='base'),
]
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    import debug_toolbar
    urlpatterns.append(
        url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    )
    urlpatterns.append(
        url(r'^__debug__/', include(debug_toolbar.urls))
    )
