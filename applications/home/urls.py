#
from django.urls import path
from . import views

app_name = "home_app"
# app_name = 'visitor_app'  # Ajusta según tu app

urlpatterns = [
    path(
        '',
        views.HomePageView.as_view(),
        name='index',
    ),

    path(
        'register-suscription',
        views.SuscriberCreateView.as_view(),
        name='add-suscription',
    ),
    path(
        'rcontact',
        views.ContactCreateView.as_view(),
        name='add-contact',
    ),
    path(
        'rcontact2',
        views.ContactCreateView2.as_view(),
        name='add-contact2',
    ),
    path(
        'sobre_mi/',
        views.AboutMe.as_view(),
        name='sobre_mi',
    ),

    path(
        'visit/',
        views.VisitorCreateView.as_view(),
        name='visit_create'
    ),


    path(
        'xxvisitaxx/',
        views.VisitorLogsView.as_view(),
        name='visitor_logs'
    ),



]