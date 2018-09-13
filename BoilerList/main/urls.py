from django.conf.urls import url
from django.contrib.auth.views import logout
from main import views

urlpatterns = [
    #user urls
    url(r'^user/?$', views.user_dash,name='user_dash'),
    url(r'^user/create/(?P<profile>[a-z]+)/?$', views.user_create,name='user_create'),
    url(r'^user/(?P<user_id>[0-9]+)/user_membership/?$', views.user_membership,name='user_membership'),
    url(r'^user/edit/?$', views.user_settings,name='user_settings'),
    #organization urls
    url(r'^organization/(?P<organization_id>[0-9]+)/dash/?$', views.organization_dash,name='organization_dash'),
    url(r'^organization/(?P<organization_id>[0-9]+)/?$', views.organization_detail,name='organization_detail'),
    url(r'^organization/create/?$', views.organization_create,name='organization_create'),
    url(r'^organization/(?P<organization_id>[0-9]+)/edit/?$', views.organization_settings,name='organization_settings'),
    #job urls
    url(r'^job/(?P<job_id>[0-9]+)/dash/?$', views.job_dash,name='job_dash'),
    url(r'^organization/(?P<organization_id>[0-9]+)/job/(?P<job_id>[0-9]+)/?$', views.jobrequest_dash,name='jobrequest_dash'),
    url(r'^job_creation$', views.job_creation,name='job_creation'),
    url(r'^job/(?P<job_id>[0-9]+)/edit/?$', views.job_settings,name='job_settings'),
    url(r'^job/status_update/$', views.job_status_update),
    url(r'^job/approve_update/$', views.job_approve_update), #when admin is made properly add this to javascript ajax 
    url(r'^job/job_delete/$', views.delete_job),
    #misc urls
    url(r'^$',views.front_page,name='front_page'),
    url(r'^search/?$',views.search,name='search'),
    url(r'^login/?$', views.login,name='login'),
    url(r'^logout/?$', logout,{'template_name':'main/logout.html'},name='logout'),
    url(r'^about/?$', views.about, name='about'),
    url(r'^quicksearch/?$', views.quicksearch,name='quicksearch'),
]

