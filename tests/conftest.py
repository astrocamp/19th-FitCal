# tests/conftest.py
import pytest

from tests.factories import (
    MemberFactory,
    OrderFactory,
    OrderItemFactory,
    ProductFactory,
    StoreFactory,
    UserFactory,
)


@pytest.fixture
def member_factory():
    return MemberFactory


@pytest.fixture
def store_factory():
    return StoreFactory


@pytest.fixture
def product_factory():
    return ProductFactory


@pytest.fixture
def user_factory():
    return UserFactory


@pytest.fixture
def order_factory():
    return OrderFactory


@pytest.fixture
def orderitem_factory():
    return OrderItemFactory
