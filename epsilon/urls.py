from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about', views.about, name='about'),
    url(r'^mentor', views.mentor, name='mentor'),
    url(r'^student', views.student, name='student'),
    url(r'^course', views.course, name='course'),
    url(r'^quiz', views.quiz, name='quiz'),
    url(r'^dashboard', views.dashboard, name='dashboard'),
    url(r'^profile', views.profile, name='profile'),
    url(r'^mycourses', views.mycourses, name='mycourses'),
    url(r'^study', views.study, name='study'),
    url(r'^group', views.group, name='group'),
    url(r'^loggedout', views.loggedout, name='loggedout'),
    url(r'^auth', views.auth, name='auth'),
    ]