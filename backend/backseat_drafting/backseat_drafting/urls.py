"""backseat_drafting URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


# In Order to include the urls with the base scaffolding, import 'include'
# from django.urls and apply the method within the python list to access
# the new routing system for the api directory. 
# We have now defined the path('') AKA 'Home Page' to be handled in the API DIR
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
]
