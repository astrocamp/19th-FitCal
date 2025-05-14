from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from users.forms import UserForm

from .forms import MemberForm
from .models import Favorite, Member, Store


def member_required(view_func):
    @wraps(view_func)
    def _wrapped_view(req, *args, **kwargs):
        if not hasattr(req.user, 'member'):
            messages.error(req, '您不是會員，無法訪問此頁面')
            return redirect('users:select_role')
        return view_func(req, *args, **kwargs)

    return login_required(_wrapped_view)


def new(req):
    form = MemberForm()
    return render(req, 'members/new.html', {'form': form})


@transaction.atomic
def create_member(request):
    user_data = request.session.get('temp_user_data')
    role = request.session.get('temp_user_role')

    if not user_data or role != 'member':
        messages.error(request, '註冊流程不完整，請重新開始')
        return redirect('users:select_role')

    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            user_form = UserForm(user_data)
            if user_form.is_valid():
                user = user_form.save(commit=False)
                user.is_active = False
                user.save()

                member = form.save(commit=False)
                member.user = user
                member.save()

                user.is_active = True
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                user.save()

                login(request, user)

                del request.session['temp_user_data']
                del request.session['temp_user_role']

                return redirect('members:show', member.id)
            else:
                messages.error(request, '帳號資料驗證失敗，請重新註冊')
                return redirect('users:sign_up')
    else:
        form = MemberForm()

    return render(request, 'members/new.html', {'form': form})


@login_required
def index(request):
    try:
        member = request.user.member
    except Member.DoesNotExist:
        return redirect('members:new')
    return render(request, 'members/index.html', {'member': member})


@member_required
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


@member_required
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


@member_required
def delete(request, id):
    member = get_object_or_404(Member, pk=id, user=request.user)
    user = request.user

    member.delete()
    return redirect('members:index')


@require_POST
def toggle_like(req, store_id):
    # member = req.user.member正常從user註冊為member的找法
    member = Member.objects.first()  # 暫時按讚都先用第一個會員來執行
    store = get_object_or_404(Store, id=store_id)
    favorite, create = Favorite.objects.get_or_create(member=member, store=store)

    if not create:
        favorite.delete()
    return redirect('stores:index')
    # return redirect(reverse('stores:index'))
    # return render(req, 'members/index.html', {'member': member, 'store': store})


def favorite_list(req):
    # member = req.user.member
    member = Member.objects.first()  # 都暫時先用第一位會員測試
    favorites = member.favorite.all()  # 拿到所有被收藏的店家

    return render(
        req,
        'members/favorite.html',
        {
            'member': member,
            'favorites': favorites,
        },
    )
