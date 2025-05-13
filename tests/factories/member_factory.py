import uuid

import factory
from faker import Faker

from members.models import Member

fake = Faker('zh_TW')


class MemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Member

    id = factory.LazyFunction(uuid.uuid4)
    phone_number = factory.LazyFunction(
        lambda: fake.phone_number().replace('-', '')[:10].rjust(10, '0')
    )
    gender = factory.Iterator(['male', 'female', 'other'])
    date_of_birth = factory.Faker('date_of_birth', minimum_age=18, maximum_age=60)
    line_id = factory.Faker('bothify', text='line_##??##')
    google_id = factory.Faker('bothify', text='google_##??##')
