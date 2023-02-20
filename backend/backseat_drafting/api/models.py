from django.db import models
from django.contrib.auth.models import User

# Create your models here.



class Category(models.Model):
    type = models.CharField(max_length=50)
    
    def __str__(self):
        return self.type


# Call this Model "Article"
class Article(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    # slug
    title = models.CharField(max_length=200)
    # excerpt
    # thumbnail
    body = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    body = models.TextField()
    user_likes = models.ManyToManyField(User, related_name="user_likes")
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:150]

class Stats(models.Model):
    PosRank = models.IntegerField(null=True)	
    Player = models.CharField(max_length=200, null=True)	
    Tm = models.CharField(max_length=200, null=True)	
    FantPos = models.CharField(max_length=200,null=True)	
    Age = models.IntegerField(null=True)	
    G = models.IntegerField(null=True)	
    GS = models.IntegerField(null=True)	
    Rushing_Att = models.IntegerField(null=True)	
    Rushing_Yds = models.IntegerField(null=True)	
    Rushing_YA = models.FloatField(null=True)	
    Rushing_TD = models.IntegerField(null=True)	
    Receiving_Tgt = models.IntegerField(null=True)	
    Receiving_Rec = models.IntegerField(null=True)	
    Receiving_Yds = models.IntegerField(null=True)	
    Receiving_YR = models.FloatField(null=True)	
    Receiving_TD = models.IntegerField(null=True)	
    Fmb = models.IntegerField(null=True)	
    FL = models.IntegerField(null=True)	
    Total_TD = models.IntegerField(null=True)	
    FantPt = models.FloatField(null=True)	
    PPR = models.FloatField(null=True)	
    
    def __str__(self):
        return self.Player