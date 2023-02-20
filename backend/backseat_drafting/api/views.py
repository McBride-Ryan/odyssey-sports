from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ArticleForm
from .models import Article, Category, Comment
import requests
from bs4 import BeautifulSoup
import pandas as pd
from django.http import JsonResponse
import numpy as np


from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Article, Stats
from .serializers import ArticleSerializer
from django.core import serializers
from django.http import HttpRequest, HttpResponseRedirect,HttpResponseBadRequest
from django.urls import reverse, reverse_lazy


def register(request):
    if request.method == 'POST':    
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email = email).exists():
                messages.info(request, 'Email is already taken!')
                return redirect('register')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already exists!')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, email = email, password = password, first_name = first_name, last_name = last_name)
                user.save()
                login(request, user)
                return redirect('home')
        else:
            messages.info(request, 'Passwords do no match')
            return redirect('register')

    else:
        return render(request, 'api/Auth/register.html')

def loginUser(request):
    if request.user.is_authenticated:
        return redirect('home')



    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password') 

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist.')

        user = authenticate(request, username=username, password=password)    

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password to not match our records.')    

    context = {}
    return render(request, 'api/Auth/login.html')    

def logoutUser(request):
    logout(request)
    return redirect('home')

def home(request):
    search = request.GET.get('search') if request.GET.get('search') != None else ''

    category = Category.objects.all()

    articles = Article.objects.filter(
        Q(category__type__icontains=search) |
        Q(title__icontains=search) |
        Q(body__icontains=search) 
        )
    
    art_json = list(Article.objects.values())
    print(type(art_json))
    # art_json = JsonResponse(data, safe=False)

    context = {'articles':articles, 'art_json':art_json, 'category': category}
    return render(request, 'api/home.html', context)

def details(request, id):
    article = Article.objects.get(id=id)
    comments = article.comment_set.all().order_by('-created')

    if request.method == 'POST':
        comment = Comment.objects.create(
            user = request.user,
            article = article,
            body = request.POST.get('body')
        )
        return redirect('details', id = article.id)

    context = {'article':article, 'comments':comments}
    return render(request, 'api/details.html', context)



def createArticle(request):
    # Bring in the Model Form and it's fields
    form = ArticleForm()
    # Check the request method for a POST
    if request.method == 'POST':
        # Capture the Request
        form = ArticleForm(request.POST)
        # Validate the Form Request
        if form.is_valid():
            # Save the Form Object
            form.save()
            # Redirect the User to the Home Page
            return redirect('home')

    context = {'form': form}
    return render(request, 'api/create.html', context)

def updateArticle(request, id):
    article = Article.objects.get(id=id)
    form = ArticleForm(instance=article)

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'api/create.html', context)

def deleteArticle(request, id):
    article = Article.objects.get(id=id)
    if request.method == 'POST':
        article.delete()
        return redirect('home')

    return render(request, 'api/delete.html', {'obj':article})

    # API CALLS

@api_view(['GET'])
def getStats(request):
    stats = requests.get('https://www.pro-football-reference.com/years/2022/fantasy.htm').text
    soup = BeautifulSoup(stats, 'lxml')
    headers = [th.getText() for th in soup.findAll('tr')[1].findAll('th')] #Find the second table row tag, find every table header column within it and extract the html text via the get_text method.
    headers = headers[1:] #Do not need the first (0 index) column header

    rows = soup.findAll('tr', class_ = lambda table_rows: table_rows != "thead") #Here we grab all rows that are not classed as table header rows - football reference throws in a table header row everyy 30 rows 
    player_stats = [[td.getText() for td in rows[i].findAll('td')] # get the table data cell text from each table data cell
                    for i in range(len(rows))] #for each row
    player_stats = player_stats[2:]
    stats = pd.DataFrame(player_stats, columns = headers)
    pos = stats.groupby('FantPos')
    gdo = pos.get_group('RB').head(50)
    gdo.head()
    gdo = gdo.drop(['Age','GS','Fmb','FL','2PM','2PP','FantPt','DKPt','FDPt','VBD','PosRank','OvRank'], axis=1)

    cols = []
    count = 1
    for column in gdo.columns:
        if column == 'Att':
            cols.append(f'Att_{count}')
            count+=1
            continue
        cols.append(column)
    gdo.columns = cols

    # rbdo
    col = []
    count = 1
    for column in gdo.columns:
        if column == 'Yds':
            col.append(f'Yds_{count}')
            count+=1
            continue
        col.append(column)
    gdo.columns = col

    co = []
    count = 1
    for column in gdo.columns:
        if column == 'TD':
            co.append(f'TD_{count}')
            count+=1
            continue
        co.append(column)
    gdo.columns = co

    gdo = gdo.replace(r'', 0, regex=True) #replace the empty string
    rbdo = gdo
    rbdo.head(1)
    rbdo['G'] = rbdo['G'].apply(pd.to_numeric, errors='coerce')
    rbdo['Cmp'] = rbdo['Cmp'].apply(pd.to_numeric, errors='coerce')
    rbdo['Att_1'] = rbdo['Att_1'].apply(pd.to_numeric, errors='coerce')
    rbdo['Yds_1'] = rbdo['Yds_1'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_1'] = rbdo['TD_1'].apply(pd.to_numeric, errors='coerce')
    rbdo['Int'] = rbdo['Int'].apply(pd.to_numeric, errors='coerce')
    rbdo['Att_2'] = rbdo['Att_2'].apply(pd.to_numeric, errors='coerce')
    rbdo['Yds_2'] = rbdo['Yds_2'].apply(pd.to_numeric, errors='coerce')
    rbdo['Y/A'] = rbdo['Y/A'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_2'] = rbdo['TD_2'].apply(pd.to_numeric, errors='coerce')
    rbdo['Tgt'] = rbdo['Tgt'].apply(pd.to_numeric, errors='coerce')
    rbdo['Rec'] = rbdo['Rec'].apply(pd.to_numeric, errors='coerce')
    rbdo['Yds_3'] = rbdo['Yds_3'].apply(pd.to_numeric, errors='coerce')
    rbdo['Y/R'] = rbdo['Y/R'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_3'] = rbdo['TD_3'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_4'] = rbdo['TD_4'].apply(pd.to_numeric, errors='coerce')
    rbdo['PPR'] = rbdo['PPR'].apply(pd.to_numeric, errors='coerce')

    rbdo['touches'] = 0

    rbdo['touches'] = rbdo['Att_2'] + rbdo['Rec']
    rbdo['Touches/G'] = rbdo['touches'] / rbdo['G']
    rbdo['Touches/G'] =  rbdo['Touches/G'].round(decimals = 1)
    rbdo['PPR/G'] = rbdo['PPR'] / rbdo['G']
    rbdo['PPR/G'] = rbdo['PPR/G'].round(decimals = 2)


    rbdo = rbdo.rename(columns={
    rbdo.columns[0]: 'Player',
    rbdo.columns[1]: 'Tm',
    rbdo.columns[2]: 'Pos',
    rbdo.columns[3]: 'G',
    rbdo.columns[4]: 'Comp',
    rbdo.columns[5]: 'Pass Att',
    rbdo.columns[6]: 'Pass Yds',
    rbdo.columns[7]: 'Pass TD',
    rbdo.columns[8]: 'Pass Int',
    rbdo.columns[9]: 'Rush Att',
    rbdo.columns[10]: 'Rush Yds',
    rbdo.columns[11]: 'Rush Y/A',
    rbdo.columns[12]: 'Rush TD',
    rbdo.columns[13]: 'Rec Tgt',
    rbdo.columns[14]: 'Rec Rec',
    rbdo.columns[15]: 'Rec Yds',
    rbdo.columns[16]: 'Rec Y/R',
    rbdo.columns[17]: 'Rec TD',
    rbdo.columns[18]: 'Total TD',
    rbdo.columns[19]: 'PPR',
    rbdo.columns[20]: 'Touches',
    rbdo.columns[21]: 'Touches/G'
    })

    
    rbdo = rbdo.drop(['Comp','Pass Att','Pass Yds', 'Pass TD', 'Pass Int'], axis=1)
    
    # rbdo.rename_axis('RK', axis='columns')
    nfl = rbdo.sort_values(by=['PPR', 'Touches'], ascending=False)
 
    nfl.reset_index(drop=True, inplace=True)
    nfl.index = np.arange(1, len(nfl) + 1)

    
    context = {
        'nfl':nfl.to_html(classes='sortable')
        }
    articles = Article.objects.all()
    serializer = ArticleSerializer(articles, many=True)
    return Response(nfl)

# Create your views here.
def statsQB(request):

    stats = requests.get('https://www.pro-football-reference.com/years/2022/fantasy.htm').text
    soup = BeautifulSoup(stats, 'lxml')
    headers = [th.getText() for th in soup.findAll('tr')[1].findAll('th')] #Find the second table row tag, find every table header column within it and extract the html text via the get_text method.
    headers = headers[1:] #Do not need the first (0 index) column header

    rows = soup.findAll('tr', class_ = lambda table_rows: table_rows != "thead") #Here we grab all rows that are not classed as table header rows - football reference throws in a table header row everyy 30 rows 
    player_stats = [[td.getText() for td in rows[i].findAll('td')] # get the table data cell text from each table data cell
                    for i in range(len(rows))] #for each row
    player_stats = player_stats[2:]
    stats = pd.DataFrame(player_stats, columns = headers)
    pos = stats.groupby('FantPos')
    gdo = pos.get_group('QB').head(30)
    gdo.head()
    gdo = gdo.drop(['Age','GS','Fmb','FL','2PM','2PP','FantPt','DKPt','FDPt','VBD','PosRank','OvRank'], axis=1)

    cols = []
    count = 1
    for column in gdo.columns:
        if column == 'Att':
            cols.append(f'Att_{count}')
            count+=1
            continue
        cols.append(column)
    gdo.columns = cols

    # rbdo
    col = []
    count = 1
    for column in gdo.columns:
        if column == 'Yds':
            col.append(f'Yds_{count}')
            count+=1
            continue
        col.append(column)
    gdo.columns = col

    co = []
    count = 1
    for column in gdo.columns:
        if column == 'TD':
            co.append(f'TD_{count}')
            count+=1
            continue
        co.append(column)
    gdo.columns = co

    gdo = gdo.replace(r'', 0, regex=True) #replace the empty string
    rbdo = gdo
    rbdo.head(1)
    rbdo['G'] = rbdo['G'].apply(pd.to_numeric, errors='coerce')
    rbdo['Cmp'] = rbdo['Cmp'].apply(pd.to_numeric, errors='coerce')
    rbdo['Att_1'] = rbdo['Att_1'].apply(pd.to_numeric, errors='coerce')
    rbdo['Yds_1'] = rbdo['Yds_1'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_1'] = rbdo['TD_1'].apply(pd.to_numeric, errors='coerce')
    rbdo['Int'] = rbdo['Int'].apply(pd.to_numeric, errors='coerce')
    rbdo['Att_2'] = rbdo['Att_2'].apply(pd.to_numeric, errors='coerce')
    rbdo['Yds_2'] = rbdo['Yds_2'].apply(pd.to_numeric, errors='coerce')
    rbdo['Y/A'] = rbdo['Y/A'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_2'] = rbdo['TD_2'].apply(pd.to_numeric, errors='coerce')
    rbdo['Tgt'] = rbdo['Tgt'].apply(pd.to_numeric, errors='coerce')
    rbdo['Rec'] = rbdo['Rec'].apply(pd.to_numeric, errors='coerce')
    rbdo['Yds_3'] = rbdo['Yds_3'].apply(pd.to_numeric, errors='coerce')
    rbdo['Y/R'] = rbdo['Y/R'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_3'] = rbdo['TD_3'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_4'] = rbdo['TD_4'].apply(pd.to_numeric, errors='coerce')
    rbdo['PPR'] = rbdo['PPR'].apply(pd.to_numeric, errors='coerce')

    rbdo['touches'] = 0

    rbdo['touches'] = rbdo['Att_2'] + rbdo['Rec']

    rbdo['Comp'] = rbdo['Cmp'] / rbdo['Att_1']
    rbdo['Comp'] =  rbdo['Comp'].round(decimals = 1)

    rbdo['Touches/G'] = rbdo['touches'] / rbdo['G']
    rbdo['Touches/G'] =  rbdo['Touches/G'].round(decimals = 1)
    rbdo['PPR/G'] = rbdo['PPR'] / rbdo['G']
    rbdo['PPR/G'] = rbdo['PPR/G'].round(decimals = 2)


    rbdo = rbdo.rename(columns={
    rbdo.columns[0]: 'Player',
    rbdo.columns[1]: 'Tm',
    rbdo.columns[2]: 'Pos',
    rbdo.columns[3]: 'G',
    rbdo.columns[4]: 'Comp',
    rbdo.columns[5]: 'Pass Att',
    rbdo.columns[6]: 'Pass Yds',
    rbdo.columns[7]: 'Pass TD',
    rbdo.columns[8]: 'Pass Int',
    rbdo.columns[9]: 'Rush Att',
    rbdo.columns[10]: 'Rush Yds',
    rbdo.columns[11]: 'Rush Y/A',
    rbdo.columns[12]: 'Rush TD',
    rbdo.columns[13]: 'Rec Tgt',
    rbdo.columns[14]: 'Rec Rec',
    rbdo.columns[15]: 'Rec Yds',
    rbdo.columns[16]: 'Rec Y/R',
    rbdo.columns[17]: 'Rec TD',
    rbdo.columns[18]: 'Total TD',
    rbdo.columns[19]: 'PPR',
    rbdo.columns[20]: 'Touches',
    rbdo.columns[21]: 'Touches/G',
    })

    
    rbdo = rbdo.drop(['Rec Tgt','Rec Rec','Rec Yds', 'Rec Y/R', 'Rec TD', 'Total TD', 'Touches', 'Touches/G'], axis=1)
    
    # rbdo.rename_axis('RK', axis='columns')
    nfl = rbdo.sort_values(by=['PPR'], ascending=False)
 
    nfl.reset_index(drop=True, inplace=True)
    nfl.index = np.arange(1, len(nfl) + 1)

    ranking = nfl.quantile([.95,.88, .75 ])
    
    context = {
        'header': 'Quarterbacks',
        'nfl':nfl.to_html(classes='sortable'),
        'ranking':ranking.to_html()
        }
    return render(request, 'api/Fantasy/stats.html', context)

def statsRB(request):

    stats = requests.get('https://www.pro-football-reference.com/years/2022/fantasy.htm').text
    soup = BeautifulSoup(stats, 'lxml')
    headers = [th.getText() for th in soup.findAll('tr')[1].findAll('th')] #Find the second table row tag, find every table header column within it and extract the html text via the get_text method.
    headers = headers[1:] #Do not need the first (0 index) column header

    rows = soup.findAll('tr', class_ = lambda table_rows: table_rows != "thead") #Here we grab all rows that are not classed as table header rows - football reference throws in a table header row everyy 30 rows 
    player_stats = [[td.getText() for td in rows[i].findAll('td')] # get the table data cell text from each table data cell
                    for i in range(len(rows))] #for each row
    player_stats = player_stats[2:]
    stats = pd.DataFrame(player_stats, columns = headers)
    pos = stats.groupby('FantPos')
    gdo = pos.get_group('RB').head(50)
    gdo.head()
    gdo = gdo.drop(['Age','GS','Fmb','FL','2PM','2PP','FantPt','DKPt','FDPt','VBD','PosRank','OvRank'], axis=1)

    cols = []
    count = 1
    for column in gdo.columns:
        if column == 'Att':
            cols.append(f'Att_{count}')
            count+=1
            continue
        cols.append(column)
    gdo.columns = cols

    # rbdo
    col = []
    count = 1
    for column in gdo.columns:
        if column == 'Yds':
            col.append(f'Yds_{count}')
            count+=1
            continue
        col.append(column)
    gdo.columns = col

    co = []
    count = 1
    for column in gdo.columns:
        if column == 'TD':
            co.append(f'TD_{count}')
            count+=1
            continue
        co.append(column)
    gdo.columns = co

    gdo = gdo.replace(r'', 0, regex=True) #replace the empty string
    rbdo = gdo
    rbdo.head(1)
    rbdo['G'] = rbdo['G'].apply(pd.to_numeric, errors='coerce')
    rbdo['Cmp'] = rbdo['Cmp'].apply(pd.to_numeric, errors='coerce')
    rbdo['Att_1'] = rbdo['Att_1'].apply(pd.to_numeric, errors='coerce')
    rbdo['Yds_1'] = rbdo['Yds_1'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_1'] = rbdo['TD_1'].apply(pd.to_numeric, errors='coerce')
    rbdo['Int'] = rbdo['Int'].apply(pd.to_numeric, errors='coerce')
    rbdo['Att_2'] = rbdo['Att_2'].apply(pd.to_numeric, errors='coerce')
    rbdo['Yds_2'] = rbdo['Yds_2'].apply(pd.to_numeric, errors='coerce')
    rbdo['Y/A'] = rbdo['Y/A'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_2'] = rbdo['TD_2'].apply(pd.to_numeric, errors='coerce')
    rbdo['Tgt'] = rbdo['Tgt'].apply(pd.to_numeric, errors='coerce')
    rbdo['Rec'] = rbdo['Rec'].apply(pd.to_numeric, errors='coerce')
    rbdo['Yds_3'] = rbdo['Yds_3'].apply(pd.to_numeric, errors='coerce')
    rbdo['Y/R'] = rbdo['Y/R'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_3'] = rbdo['TD_3'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_4'] = rbdo['TD_4'].apply(pd.to_numeric, errors='coerce')
    rbdo['PPR'] = rbdo['PPR'].apply(pd.to_numeric, errors='coerce')

    rbdo['touches'] = 0

    rbdo['touches'] = rbdo['Att_2'] + rbdo['Rec']
    rbdo['Touches/G'] = rbdo['touches'] / rbdo['G']
    rbdo['Touches/G'] =  rbdo['Touches/G'].round(decimals = 1)
    rbdo['PPR/G'] = rbdo['PPR'] / rbdo['G']
    rbdo['PPR/G'] = rbdo['PPR/G'].round(decimals = 2)


    rbdo = rbdo.rename(columns={
    rbdo.columns[0]: 'Player',
    rbdo.columns[1]: 'Tm',
    rbdo.columns[2]: 'Pos',
    rbdo.columns[3]: 'G',
    rbdo.columns[4]: 'Comp',
    rbdo.columns[5]: 'Pass Att',
    rbdo.columns[6]: 'Pass Yds',
    rbdo.columns[7]: 'Pass TD',
    rbdo.columns[8]: 'Pass Int',
    rbdo.columns[9]: 'Rush Att',
    rbdo.columns[10]: 'Rush Yds',
    rbdo.columns[11]: 'Rush Y/A',
    rbdo.columns[12]: 'Rush TD',
    rbdo.columns[13]: 'Rec Tgt',
    rbdo.columns[14]: 'Rec Rec',
    rbdo.columns[15]: 'Rec Yds',
    rbdo.columns[16]: 'Rec Y/R',
    rbdo.columns[17]: 'Rec TD',
    rbdo.columns[18]: 'Total TD',
    rbdo.columns[19]: 'PPR',
    rbdo.columns[20]: 'Touches',
    rbdo.columns[21]: 'Touches/G'
    })

    
    rbdo = rbdo.drop(['Comp','Pass Att','Pass Yds', 'Pass TD', 'Pass Int'], axis=1)
    
    # rbdo.rename_axis('RK', axis='columns')
    nfl = rbdo.sort_values(by=['PPR', 'Touches'], ascending=False)
 
    nfl.reset_index(drop=True, inplace=True)
    nfl.index = np.arange(1, len(nfl) + 1)

    ranking = nfl.quantile([.95,.88, .75 ])
    
    context = {
        'header': 'Running Backs',
        'nfl':nfl.to_html(classes='sortable'),
        'ranking':ranking.to_html()
        }
    return render(request, 'api/Fantasy/stats.html', context)

def statsWR(request):

    stats = requests.get('https://www.pro-football-reference.com/years/2022/fantasy.htm').text
    soup = BeautifulSoup(stats, 'lxml')
    headers = [th.getText() for th in soup.findAll('tr')[1].findAll('th')] #Find the second table row tag, find every table header column within it and extract the html text via the get_text method.
    headers = headers[1:] #Do not need the first (0 index) column header

    rows = soup.findAll('tr', class_ = lambda table_rows: table_rows != "thead") #Here we grab all rows that are not classed as table header rows - football reference throws in a table header row everyy 30 rows 
    player_stats = [[td.getText() for td in rows[i].findAll('td')] # get the table data cell text from each table data cell
                    for i in range(len(rows))] #for each row
    player_stats = player_stats[2:]
    stats = pd.DataFrame(player_stats, columns = headers)
    pos = stats.groupby('FantPos')
    gdo = pos.get_group('WR').head(60)
    gdo = gdo.drop(['Age','GS','Fmb','FL','2PM','2PP','FantPt','DKPt','FDPt','VBD','PosRank','OvRank'], axis=1)

    cols = []
    count = 1
    for column in gdo.columns:
        if column == 'Att':
            cols.append(f'Att_{count}')
            count+=1
            continue
        cols.append(column)
    gdo.columns = cols

    # rbdo
    col = []
    count = 1
    for column in gdo.columns:
        if column == 'Yds':
            col.append(f'Yds_{count}')
            count+=1
            continue
        col.append(column)
    gdo.columns = col

    co = []
    count = 1
    for column in gdo.columns:
        if column == 'TD':
            co.append(f'TD_{count}')
            count+=1
            continue
        co.append(column)
    gdo.columns = co

    gdo = gdo.replace(r'', 0, regex=True) #replace the empty string
    rbdo = gdo
    
    rbdo['G'] = rbdo['G'].apply(pd.to_numeric, errors='coerce')
    rbdo['Cmp'] = rbdo['Cmp'].apply(pd.to_numeric, errors='coerce')
    rbdo['Att_1'] = rbdo['Att_1'].apply(pd.to_numeric, errors='coerce')
    rbdo['Yds_1'] = rbdo['Yds_1'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_1'] = rbdo['TD_1'].apply(pd.to_numeric, errors='coerce')
    rbdo['Int'] = rbdo['Int'].apply(pd.to_numeric, errors='coerce')
    rbdo['Att_2'] = rbdo['Att_2'].apply(pd.to_numeric, errors='coerce')
    rbdo['Yds_2'] = rbdo['Yds_2'].apply(pd.to_numeric, errors='coerce')
    rbdo['Y/A'] = rbdo['Y/A'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_2'] = rbdo['TD_2'].apply(pd.to_numeric, errors='coerce')
    rbdo['Tgt'] = rbdo['Tgt'].apply(pd.to_numeric, errors='coerce')
    rbdo['Rec'] = rbdo['Rec'].apply(pd.to_numeric, errors='coerce')
    rbdo['Yds_3'] = rbdo['Yds_3'].apply(pd.to_numeric, errors='coerce')
    rbdo['Y/R'] = rbdo['Y/R'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_3'] = rbdo['TD_3'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_4'] = rbdo['TD_4'].apply(pd.to_numeric, errors='coerce')
    rbdo['PPR'] = rbdo['PPR'].apply(pd.to_numeric, errors='coerce')

    rbdo['touches'] = 0

    rbdo['touches'] = rbdo['Att_2'] + rbdo['Rec']
    rbdo['Touches/G'] = rbdo['touches'] / rbdo['G']
    rbdo['Touches/G'] =  rbdo['Touches/G'].round(decimals = 1)
    rbdo['PPR/G'] = rbdo['PPR'] / rbdo['G']
    rbdo['PPR/G'] = rbdo['PPR/G'].round(decimals = 2)


    rbdo = rbdo.rename(columns={
    rbdo.columns[0]: 'Player',
    rbdo.columns[1]: 'Tm',
    rbdo.columns[2]: 'Pos',
    rbdo.columns[3]: 'G',
    rbdo.columns[4]: 'Comp',
    rbdo.columns[5]: 'Pass Att',
    rbdo.columns[6]: 'Pass Yds',
    rbdo.columns[7]: 'Pass TD',
    rbdo.columns[8]: 'Pass Int',
    rbdo.columns[9]: 'Rush Att',
    rbdo.columns[10]: 'Rush Yds',
    rbdo.columns[11]: 'Rush Y/A',
    rbdo.columns[12]: 'Rush TD',
    rbdo.columns[13]: 'Rec Tgt',
    rbdo.columns[14]: 'Rec Rec',
    rbdo.columns[15]: 'Rec Yds',
    rbdo.columns[16]: 'Rec Y/R',
    rbdo.columns[17]: 'Rec TD',
    rbdo.columns[18]: 'Total TD',
    rbdo.columns[19]: 'PPR',
    rbdo.columns[20]: 'Touches',
    rbdo.columns[21]: 'Touches/G'
    })

    
    rbdo = rbdo.drop(['Comp','Pass Att','Pass Yds', 'Pass TD', 'Pass Int'], axis=1)
    
    nfl = rbdo.sort_values(by=['PPR', 'Touches'], ascending=False)
 
    nfl.reset_index(drop=True, inplace=True)
    nfl.index = np.arange(1, len(nfl) + 1)

    ranking = nfl.quantile([.95,.88, .75 ])
    
    context = {
        'header': 'Wide receivers',
        'nfl':nfl.to_html(classes='sortable'),
        'ranking':ranking.to_html()
        }
    return render(request, 'api/Fantasy/stats.html', context)

def statsTE(request):
    stats = requests.get('https://www.pro-football-reference.com/years/2022/fantasy.htm').text
    soup = BeautifulSoup(stats, 'lxml')
    headers = [th.getText() for th in soup.findAll('tr')[1].findAll('th')] #Find the second table row tag, find every table header column within it and extract the html text via the get_text method.
    headers = headers[1:] #Do not need the first (0 index) column header

    rows = soup.findAll('tr', class_ = lambda table_rows: table_rows != "thead") #Here we grab all rows that are not classed as table header rows - football reference throws in a table header row everyy 30 rows 
    player_stats = [[td.getText() for td in rows[i].findAll('td')] # get the table data cell text from each table data cell
                    for i in range(len(rows))] #for each row
    player_stats = player_stats[2:]
    stats = pd.DataFrame(player_stats, columns = headers)
    pos = stats.groupby('FantPos')
    gdo = pos.get_group('TE').head(30)
    gdo = gdo.drop(['Age','GS','Fmb','FL','2PM','2PP','FantPt','DKPt','FDPt','VBD','PosRank','OvRank'], axis=1)

    cols = []
    count = 1
    for column in gdo.columns:
        if column == 'Att':
            cols.append(f'Att_{count}')
            count+=1
            continue
        cols.append(column)
    gdo.columns = cols

    # rbdo
    col = []
    count = 1
    for column in gdo.columns:
        if column == 'Yds':
            col.append(f'Yds_{count}')
            count+=1
            continue
        col.append(column)
    gdo.columns = col

    co = []
    count = 1
    for column in gdo.columns:
        if column == 'TD':
            co.append(f'TD_{count}')
            count+=1
            continue
        co.append(column)
    gdo.columns = co

    gdo = gdo.replace(r'', 0, regex=True) #replace the empty string
    rbdo = gdo
    
    rbdo['G'] = rbdo['G'].apply(pd.to_numeric, errors='coerce')
    rbdo['Cmp'] = rbdo['Cmp'].apply(pd.to_numeric, errors='coerce')
    rbdo['Att_1'] = rbdo['Att_1'].apply(pd.to_numeric, errors='coerce')
    rbdo['Yds_1'] = rbdo['Yds_1'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_1'] = rbdo['TD_1'].apply(pd.to_numeric, errors='coerce')
    rbdo['Int'] = rbdo['Int'].apply(pd.to_numeric, errors='coerce')
    rbdo['Att_2'] = rbdo['Att_2'].apply(pd.to_numeric, errors='coerce')
    rbdo['Yds_2'] = rbdo['Yds_2'].apply(pd.to_numeric, errors='coerce')
    rbdo['Y/A'] = rbdo['Y/A'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_2'] = rbdo['TD_2'].apply(pd.to_numeric, errors='coerce')
    rbdo['Tgt'] = rbdo['Tgt'].apply(pd.to_numeric, errors='coerce')
    rbdo['Rec'] = rbdo['Rec'].apply(pd.to_numeric, errors='coerce')
    rbdo['Yds_3'] = rbdo['Yds_3'].apply(pd.to_numeric, errors='coerce')
    rbdo['Y/R'] = rbdo['Y/R'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_3'] = rbdo['TD_3'].apply(pd.to_numeric, errors='coerce')
    rbdo['TD_4'] = rbdo['TD_4'].apply(pd.to_numeric, errors='coerce')
    rbdo['PPR'] = rbdo['PPR'].apply(pd.to_numeric, errors='coerce')

    rbdo['touches'] = 0

    rbdo['touches'] = rbdo['Att_2'] + rbdo['Rec']
    rbdo['Touches/G'] = rbdo['touches'] / rbdo['G']
    rbdo['Touches/G'] =  rbdo['Touches/G'].round(decimals = 1)
    rbdo['PPR/G'] = rbdo['PPR'] / rbdo['G']
    rbdo['PPR/G'] = rbdo['PPR/G'].round(decimals = 2)


    rbdo = rbdo.rename(columns={
    rbdo.columns[0]: 'Player',
    rbdo.columns[1]: 'Tm',
    rbdo.columns[2]: 'Pos',
    rbdo.columns[3]: 'G',
    rbdo.columns[4]: 'Comp',
    rbdo.columns[5]: 'Pass Att',
    rbdo.columns[6]: 'Pass Yds',
    rbdo.columns[7]: 'Pass TD',
    rbdo.columns[8]: 'Pass Int',
    rbdo.columns[9]: 'Rush Att',
    rbdo.columns[10]: 'Rush Yds',
    rbdo.columns[11]: 'Rush Y/A',
    rbdo.columns[12]: 'Rush TD',
    rbdo.columns[13]: 'Rec Tgt',
    rbdo.columns[14]: 'Rec Rec',
    rbdo.columns[15]: 'Rec Yds',
    rbdo.columns[16]: 'Rec Y/R',
    rbdo.columns[17]: 'Rec TD',
    rbdo.columns[18]: 'Total TD',
    rbdo.columns[19]: 'PPR',
    rbdo.columns[20]: 'Touches',
    rbdo.columns[21]: 'Touches/G'
    })

    
    rbdo = rbdo.drop(['Comp','Pass Att','Pass Yds', 'Pass TD', 'Pass Int'], axis=1)
    
    nfl = rbdo.sort_values(by=['PPR', 'Touches'], ascending=False)
 
    nfl.reset_index(drop=True, inplace=True)
    nfl.index = np.arange(1, len(nfl) + 1)

    ranking = nfl.quantile([.95,.88, .75 ])
    
    context = {
        'header': 'Tight Ends',
        'nfl':nfl.to_html(classes='sortable'),
        'ranking':ranking.to_html()
        }
    return render(request, 'api/Fantasy/stats.html', context)

def test(request):
    todos = list(Stats.objects.all().values())
    return JsonResponse({'context': todos})