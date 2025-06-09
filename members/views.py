from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from common.decorator import member_required
from stores.models import Store

from .forms import MemberForm
from .models import Member


def new(request):
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        request.session['next_url'] = next_url

    form = MemberForm()
    return render(request, 'members/new.html', {'form': form})


@transaction.atomic
def create_member(request):
    if request.method == 'POST' and request.user.is_member:
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.user = request.user
            member.save()
            next_url = request.session.pop('next_url', None)
            messages.success(request, '新增會員資料成功')
            return redirect(next_url or 'members:show', id=member.id)
        else:
            messages.error(request, _('請檢查輸入內容'))
            return render(request, 'members/new.html', {'form': form}, status=400)
    return redirect('stores:index')


@member_required
def index(request):
    member = Member.objects.filter(user=request.user).first()
    return render(request, 'members/index.html', {'member': member})


@member_required
def show(request, id):
    member = get_object_or_404(Member, pk=id, user=request.user)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect('members:show', id=member.id)
        return render(request, 'members/edit.html', {'member': member, 'form': form})
    return render(request, 'members/index.html', {'member': member})


@member_required
def edit(request, id):
    member = get_object_or_404(Member, pk=id, user=request.user)
    form = MemberForm(instance=member)
    return render(request, 'members/edit.html', {'form': form, 'member': member})


@member_required
def delete(request, id):
    member = get_object_or_404(Member, pk=id, user=request.user)
    member.delete()
    return redirect('users:index')


@require_POST
@member_required
def favorite(req, store_id):
    member = req.user.member
    favorites = member.favorite
    store = get_object_or_404(Store, id=store_id)

    if favorites.filter(pk=store.pk).exists():
        favorites.remove(store)
    else:
        favorites.add(store)
    return render(req, 'shared/favorite_btn.html', {'member': member, 'store': store})


@member_required
def favorite_list(req):
    member = req.user.member
    favorites = member.favorite.all()  # 拿到所有被收藏的店家

    return render(
        req,
        'members/favorite.html',
        {
            'member': member,
            'favorites': favorites,
        },
    )


@member_required
def collections(request):
    member = request.user.member
    collections = member.favorite_products.all()
    return render(
        request,
        'members/collections.html',
        {
            'member': member,
            'collections': collections,
        },
    )
