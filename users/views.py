from django.shortcuts import render

# Create your views here.
def sign_in(req):
    return render(req, "users/sign_in.html")

def sign_up(req):
    return render(req, "users/sign_up.html")