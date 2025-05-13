# tests/conftest.py
import pytest

from tests.factories import (
    MemberFactory,
    OrderFactory,
    ProductFactory,
    StoreFactory,
)


@pytest.fixture
def member_factory():
    return MemberFactory


@pytest.fixture
def store_factory():
    return StoreFactory


@pytest.fixture
def product_factory():
    return ProductFactory()


@pytest.fixture
def order_factory(member_factory, store_factory):
    def factory(**kwargs):
        defaults = {
            'member': member_factory(),
            'store': store_factory(),
        }
        defaults.update(kwargs)
        return OrderFactory(**defaults)

    return factory
