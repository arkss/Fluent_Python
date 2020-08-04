from abc import ABC, abstractmethod
from collections import namedtuple

Customer = namedtuple('Customer', 'name fidelity')


class LineItem:

    def __init__(self, product, quantity, price):
        self.product = product
        self.quantity = quantity
        self.price = price

    def total(self):
        return self.price * self.quantity


class Order:  # 콘텍스트
    def __init__(self, customer, cart, promotion=None):
        self.customer = customer
        self.cart = list(cart)
        self.promotion = promotion

    def total(self):
        if not hasattr(self, '__total'):
            self.__total = sum(item.total() for item in self.cart)
        return self.__total

        def due(self):
            if self.promotion is None:
                discount = 0
            else:
                discount = self.promotion.discount(self)
            return self.total() - discount

        def __repr__(self):
            fmt = '<Order total: {:.2f} due: {:.2f}'
            return fmt.format(self.total(), self.due())


class Promotion(ABC):  # 전략: 추상 베이스 클래스

    @abstractmethod
    def discount(self, order):
        """할인액을 구체적인 숫자로 반환한다"""


class FidelityPromo(Promotion):
    """충성도 포인트가 1000점 이상인 고객에게 전체 5% 할인 적용"""

    def discount(self, order):
        return order.total() * .05 if order.customer.fidelity >= 1000 else 0


class BulkItemPromo(Promotion):
    """20개 이상의 동일 상품을 구입하면 10% 할인 적용"""

    def discount(self, order):
        discount = 0
        for item in order.cart:
            if item.quantity >= 20:
                discount += item.total() * .1
        return discount


class LargeOderPromo(Promotion):
    """10종류 이상의 상품을 구입하면 전체 7% 할인 적용"""

    def discount(self, order):
        distinct_items = {item.product for item in order.cart}
        if len(distinct_items) >= 10:
            return order.total * .07
        return 0
