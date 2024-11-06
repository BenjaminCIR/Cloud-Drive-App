from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='polls/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('statistics/', views.statistics, name='statistics'),
    path('success/', views.success, name='success'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('delete_file/', views.delete_file, name='delete_file'),
    path('rename_file/', views.rename_file, name='rename_file'),
    path('move_file/', views.move_file, name='move_file'),
    path('create_folder/', views.create_folder, name='create_folder'),
    path('delete_folder/', views.delete_folder, name='delete_folder'),
    path('rename_folder/', views.rename_folder, name='rename_folder'),
    path('move_folder/', views.move_folder, name='move_folder'),
    path('choose_folder/', views.choose_folder, name='choose_folder'),
]