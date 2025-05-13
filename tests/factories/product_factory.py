import uuid

import factory

from products.models import Product


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker('word')
    description = factory.Faker('sentence')
    calories = factory.Faker('random_int', min=50, max=800)
    quantity = factory.Faker('random_int', min=1, max=50)
    price = factory.Faker('random_int', min=50, max=1000)
    customize = factory.Faker('sentence', nb_words=5)
