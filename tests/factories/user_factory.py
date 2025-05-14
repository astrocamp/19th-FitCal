import factory
from django.contrib.auth import get_user_model


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        skip_postgeneration_save = True

    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword123')
    is_staff = False
    is_superuser = False
