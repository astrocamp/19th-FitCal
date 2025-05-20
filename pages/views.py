from django.shortcuts import redirect


def index(request):
    return redirect('users:sign_in')
