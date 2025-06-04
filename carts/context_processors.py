from .models import Cart


def cart_count(request):
    if request.user.is_authenticated and request.user.is_member:
        member = request.user.member
        count = Cart.objects.filter(member=member).count()
    else:
        count = 0

    return {'cart_count': count}
