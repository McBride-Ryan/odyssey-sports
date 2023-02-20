from django.contrib import admin

# Register your models here.
from .models import Article, Category, Comment

admin.site.register(Article)
admin.site.register(Category)
admin.site.register(Comment)