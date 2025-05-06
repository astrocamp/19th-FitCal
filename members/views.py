from django.shortcuts import get_object_or_404, redirect, render

from .forms import MemberForm
from .models import Member


# Create your views here.
def index(request):
    members = Member.objects.order_by('-created_at')
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('members:index')
        else:
            return render(request, 'members/new.html', {'form': form})
    return render(request, 'members/index.html', {'members': members})


def new(request):
    form = MemberForm()
    return render(request, 'members/new.html', {'form': form})


def show(request, id):
    member = get_object_or_404(Member, id=id)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect('members:show', id)
        else:
            return render(request, 'members/edit.html', {'form': form})
    return render(request, 'members/show.html', {'member': member})


def edit(request, id):
    member = get_object_or_404(Member, id=id)
    form = MemberForm(instance=member)
    return render(request, 'members/edit.html', {'member': member, 'form': form})


def delete(request, id):
    member = get_object_or_404(Member, id=id)
    member.delete()
    return redirect('members:index')
