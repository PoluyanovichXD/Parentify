from django.shortcuts import render

def home(request):
    return render(request, 'pages/map/home.html')