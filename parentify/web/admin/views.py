from django.shortcuts import render


def home(request):
    return render(request, 'pages/admin/home.html')