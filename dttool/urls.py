from . import views
from django.conf.urls import url
from django.contrib.auth.views import password_reset,password_reset_done, password_reset_confirm, password_reset_complete

app_name = 'dttool'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^generate_report$', views.generate_report, name='generate_report'),
    url(r'^change_password/$', views.change_password, name='change_password'),
    url(r'^password_reset/$', password_reset,{'email_template_name':'dttool/registration/password_reset_email.html',
                                                    'template_name':'dttool/registration/password_reset_form.html',
                                                    'subject_template_name':'dttool/registration/password_reset_subject.txt',
                                                    'post_reset_redirect':'dttool:password_reset_done',
                                                    'from_email':'myapp@django.com',
                                                    },name='password_reset'),

    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', password_reset_confirm,
                                                    {'template_name': 'dttool/registration/password_reset_confirm.html',
                                                    'post_reset_redirect': 'dttool:password_reset_complete'},
                                                    name='password_reset_confirm'),
    url(r'^password_reset/done/$', password_reset_done, {'template_name': 'dttool/registration/password_reset_done.html'}, name='password_reset_done'),
    url(r'^reset/done/$', password_reset_complete, {'template_name': 'dttool/registration/password_reset_complete.html'},name='password_reset_complete'),

]
