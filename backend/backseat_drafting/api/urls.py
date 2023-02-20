from django.urls import path, include
#Accessing the same directory by means of '.' in 'api'
from . import views

#We can access the Urls through the Function Based views defined in views.py
urlpatterns = [
    path('', views.home, name='home'),
    path('details/<str:id>/', views.details, name='details'),

    # API CALLS
    path('stats/quarterbacks/', views.statsQB, name='statsQB'),
    path('stats/running-backs/', views.statsRB, name='statsRB'),
    path('stats/wide-receivers/', views.statsWR, name='statsWR'),
    path('stats/tight-ends/', views.statsTE, name='statsTE'),

    path('register/', views.register, name='register'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    

    path('create-article/', views.createArticle, name='createArticle'),
    path('update-article/<str:id>/', views.updateArticle, name='updateArticle'),
    path('delete-article/<str:id>/', views.deleteArticle, name='deleteArticle'),

    path('test', views.test, name='test'),
]
