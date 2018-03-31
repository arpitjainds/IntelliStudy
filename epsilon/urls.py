from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about', views.about, name='about'),
    url(r'^mentor', views.mentor, name='mentor'),
    url(r'^student', views.student, name='student'),
    url(r'^course', views.course, name='course'),
    url(r'^career', views.career, name='career'),
    url(r'^quiz', views.quiz, name='quiz'),
    url(r'^dashboard', views.dashboard, name='dashboard'),
    url(r'^profile', views.profile, name='profile'),
    url(r'^update_profile', views.update_profile, name='update_profile'),
    url(r'^mycourses', views.mycourses, name='mycourses'),
    url(r'^study', views.study, name='study'),
    url(r'^loggedout', views.loggedout, name='loggedout'),
    url(r'^auth', views.auth, name='auth'),
    url(r'^signup', views.signup, name='signup'),
    url(r'^mdashboard', views.mdashboard, name='mdashboard'),
    url(r'^manage', views.manage, name='manage'),
    url(r'^edittopic', views.edittopic, name='edittopic'),
    url(r'^editquiz', views.editquiz, name='editquiz'),
    url(r'^editcourse', views.editcourse, name='editcourse'),
    url(r'^apt', views.apt, name='apt'),
    url(r'^reco', views.reco, name='reco'),
    ]
