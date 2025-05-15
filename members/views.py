from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MemberForm
from .models import Member


@login_required
def index(request):
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        member = None

    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member, is_create=not bool(member))
        if form.is_valid():
            member = form.save(commit=False)
            member.user = request.user
            member.save()
            return redirect('members:show', member.id)
        else:
            return render(request, 'members/new.html', {'form': form})
    else:
        if member:
            return render(request, 'members/index.html', {'member': member})
        else:
            form = MemberForm(is_create=True)
            return render(request, 'members/new.html', {'form': form})


@login_required
def new(request):
    form = MemberForm(is_create=True)
    return render(request, 'members/new.html', {'form': form})


@login_required
def show(request, id):
    member = get_object_or_404(Member, pk=id, user=request.user)

    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect('members:show', member.id)
        return render(request, 'members/show.html', {'member': member, 'form': form})

    else:
        form = MemberForm(instance=member)

        return render(request, 'members/show.html', {'member': member, 'form': form})


@login_required
def edit(request, id):
    member = get_object_or_404(Member, pk=id, user=request.user)

    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect('members:show', member.id)
        else:
            return render(
                request, 'members/edit.html', {'form': form, 'member': member}
            )
    else:
        form = MemberForm(instance=member)
        return render(request, 'members/edit.html', {'form': form, 'member': member})


@login_required
def delete(request, id):
    member = get_object_or_404(Member, pk=id, user=request.user)
    user = request.user

    member.delete()
    user.delete()
    logout(request)

    return redirect('users:sign_up')
