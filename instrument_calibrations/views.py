from django.http import HttpResponse
from django.shortcuts import render

# construct views
def home(request):
    return render(request, 'homepage2.html')

def terms(request):
    return render(request, 'terms_conditions.html')