from .models import Cart


def cart_count(request):
    if request.user.is_authenticated and hasattr(request.user, 'member'):
        member = request.user.member
        count = Cart.objects.filter(member=member).count()
    else:
        count = 0

    return {'cart_count': count}
