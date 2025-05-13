import factory
from django.contrib.auth import get_user_model
from factory import LazyAttribute


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword123')
    is_staff = factory.LazyAttribute(lambda o: False)
    is_superuser = factory.LazyAttribute(lambda o: False)

    @factory.post_generation
    def set_password(obj, create, extracted, **kwargs):
        if not extracted:
            obj.set_password('defaultpassword123')  # Default password
