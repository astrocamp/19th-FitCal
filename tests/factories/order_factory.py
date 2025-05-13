import uuid
from datetime import datetime
from decimal import Decimal

import factory
from django.utils import timezone

from orders.models import Order, OrderItem
from tests.factories.member_factory import MemberFactory
from tests.factories.product_factory import ProductFactory
from tests.factories.store_factory import StoreFactory


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    id = factory.LazyFunction(uuid.uuid4)
    member = factory.SubFactory(MemberFactory)
    store = factory.SubFactory(StoreFactory)
    pickup_time = factory.LazyFunction(lambda: timezone.now())
    note = factory.Faker('text', max_nb_chars=200)
    order_status = 'pending'
    payment_method = 'cash'
    payment_status = 'unpaid'
    total_price = Decimal(1000)
    customize = {}
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    id = factory.LazyFunction(uuid.uuid4)
    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    product_name = factory.Faker('word')
    unit_price = Decimal(200)
    quantity = 1
    subtotal = factory.LazyAttribute(lambda obj: obj.unit_price * obj.quantity)
