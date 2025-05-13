import uuid

import factory

from stores.models import Store


class StoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Store

    id = factory.LazyFunction(uuid.uuid4)
    address = factory.Faker('address')
    phone_number = '0912345678'
    opening_time = factory.Faker('time_object')
    closing_time = factory.Faker('time_object')
    tax_id = factory.Faker('bothify', text='########')  # 8位數字
