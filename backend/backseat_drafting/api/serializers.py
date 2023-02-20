from rest_framework import serializers
from .models import Article, Stats

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
         
class StatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stats
        fields = '__all__'