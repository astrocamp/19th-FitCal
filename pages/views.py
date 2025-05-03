from django.shortcuts import render
from django.contrib import messages

# Create your views here.

def home(req):
    messages.success(req, "success")#
    return render(req, "pages/home.html")