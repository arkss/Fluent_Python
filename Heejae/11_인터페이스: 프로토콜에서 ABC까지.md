# 11 인터페이스: 프로토콜에서 ABC까지

- 추상 클래스는 인터페이스를 표현한다.

- 추상 베이스 클래스(ABC)는 구현이 인터페이스에 따르는지 검증한다.

## 11.1 파이썬 문화에서의 인터페이스와 프로토콜

파이썬 언어의 모든 클래스는 ABC에 상관 없이 인터페이스를 가지고 있다.
클래스가 상속하거나 구현한 공개 속성(메서드나 데이터 속성)들의 집합이 인터페이스다.

참고로 보호된 속성과 비공개 속성은 인터페이스에 속하지 않는다고 정의하고 이것은 관례다.

인터페이스의 정의에 대해서는 '시스템에서 어떤 역할을 할 수 있게 해주는 객체의 공개 메서드의 일부'라고 보충할 수 있다.

어떤 역할을 완수하기 위한 메서드의 집합으로서의 인터페이스를 프로토콜이라고 불렀다. 예를들어 시퀀스 같은 객체를 만들기 위해 `__len__`과 `__getitem__`을 구현하는데 이 메서드를 프로토콜이라고 한다.

'x와 같은 객체', 'x 프로토콜', 'x 인터페이스'는 파이썬 영역 안에서 동의어이다.

## 11.2 파이썬은 시퀀스를 찾아낸다

Foo 클래스 예제를 보자. 여기서 주의 할 점은 Foo 클래스는 `abc.Sequence`를 상속하지 않으며, 프로토콜 메서드 중 `__getitem__()` 메서드 하나만 구현한다.

```python
>>> class Foo:
...     def __getitem__(self, pos):
...             return range(0, 30, 10)[pos]
...
>>> f = Foo()
>>> f[1]
10
>>> for i in f: print(i)
...
0
10
20
>>> 20 in f
True
>>> 15 in f
False
```

`__iter__()` 메서드는 구현되지 않았지만, `__getitem__()` 메서드가 구현되어 있으므로 Foo 객체를 반복할 수 있다.(파이썬 인터프리터는 0부터 시작하는 정수 인덱스로 `__getitem__()` 메서드를 호출하여 객체 반복을 시도한다.)

반복은 덕 타이핑의 극단적인 예이다.

## 11.3 런타임에 프로토콜을 구현하는 멍키 패칭

```python
import collections

Card = collections.namedtuple('Card', ['rank', 'suit'])

class FrenchDeck:
    ranks = [str(n) for n in range(2,11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()


    def __init__(self):
        self._cards = [Card(rank, suit) for suit in self.suits
                                        for rank in self.ranks]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]
```

FrenchDeck 클래스를 섞기 위해 `shuffle()` 함수를 쓰면 아래와 같은 에러가 발생한다.

```python
>>> from random import shuffle
>>> deck = FrenchDeck()
>>> shuffle(deck)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/maru/.pyenv/versions/3.8.1/lib/python3.8/random.py", line 307, in shuffle
    x[i], x[j] = x[j], x[i]
TypeError: 'FrenchDeck' object does not support item assignment
```

FrenchDeck 객체가 할당을 지원하지 않기 때문에, 즉 불변 시퀀스 프로토콜만 구현하고 있기 때문이다. 가변 시퀀스는 `__setitem__()` 메서드도 지원해야 한다.

파이썬은 동적 언어이므로 코드를 대화형 콘솔에서 실행하는 동안에 수정 할 수 있다.

```python
>>> def set_card(deck, position, card):
...     deck._cards[position] = card
...
>>> FrenchDeck.__setitem__ = set_card # monkey patching : 소스 코드를 건드리지 않고 런타임에 클래스나 모듈을 변경하는 행위
>>> shuffle(deck)
>>> deck[:5]
[Card(rank='10', suit='spades'), Card(rank='2', suit='diamonds'), Card(rank='A', suit='clubs'), Card(rank='6', suit='spades'), Card(rank='A', suit='spades')]
```

위의 예제는 멍키 패칭 말고도 프로토콜이 동적이라는 것을 보여준다.

_`random.shuffle()` 함수는 자신이 받는 인수의 자료형에 대해서는 신경 쓰지 않는다. 단지 받은 객체가 일부 가변 시퀀스 프로토콜을 구현하고 있으면 될 뿐이다. 심지어 해당 객체가 필요한 메서드를 '원래부터' 가지고 있었는지, 아니면 나중에 얻었는지는 전혀 문제가 되지 않는다._

<br>
- 참고 : [동적과 정적 각각의 장점](https://softwareengineering.stackexchange.com/a/122212)

## 11.4 알렉스 마르텔리의 물새

- 동일한 이름의 메서드를 호출한다고 해서 의미가 비슷하다고 생각할 수 없다. 그것보다 어느 정도의 유사성을 긍정적으로 주장할 수 있어야 한다.

- 비슷한 모습과 행동을 하는 것보다 공유하는 조상이 더 가까운지 중요하다. 거위 예를 들어서 덕 타이핑 보다는 구스 타이핑이라는 표현을 쓰겠다

- 구스 타이핑이라는 말은 cls가 추상 베이스 클래스인 경우, 즉 cls의 메타클래스(클래스를 만드는 클래스)가 abc.ABCMeta인 경우에는 isinstance(obj, cls)를 써도 좋다는 것을 의미한다.

- 클래스를 ABC의 서브클래스로 인식시키기 위해 등록할 필요가 없는 경우도 있다. 아래 예제를 보자.

```python
>>> class Struggle:
...     def __len__(self): return 23
...
>>> from collections import abc
>>> isinstance(Struggle(), abc.Sized)
True
```

단지 `__len__()`이라는 특별 메서드만 구현하면 되며, 등록할 필요 없이 Struggle은 abc.Sized의 일종의 서브클래스로 인식된다.

- numbers, collections.abc, 혹은 다른 프레임워크에 있는 ABC가 표현하는 개념을 실현하는 클래스를 구현할 때는 언제나 해당 ABC를 상속하거나 해당 ABC에 등록하라. 필요한 메서드를 구현하는 것보다 낫다. 상속은 개발자의 의도를 명확히 나타낸다.

- 이 과정을 빠뜨린 클래스를 정의한 라이브러리나 프레임워크를 사용하는 프로그램에서는 언제나 코드 시작 부분에서 여러분이 클래스를 직접 등록하고 `isinstance`로 검사를 해야 한다.

- 그리고 배포용 코드에서 절대로 ABC나 메타클래스를 직접 구현하지 **말아야 한다.**

- isinstance()를 너무 많이 사용하는 것은 코드 악취일 수 있다.

- isinstance()보다 아래 예제처럼 덕 타이핑을 이용해도 좋다. [collections.namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple)에서 field_names 인수 처리를 하는 흉내 내는 아래 코드를 보자.

```python
try:
    field_names = field_names.replace(',', ' ').split() # field_names를 문자열이라고 가정한다.
except AttributeError: # 문자열이 아니므로 이제 field_names는 반복형이다.
    pass

field_names = tuple(field_names)
```

문서에서는 field_names는 string의 시퀀스 또는 구분자를 가진 단일 string을 받는다고 한다. 실제로 int 또는 boolean등을 넣으면 `<자료형> object is not iterable` 메세지를 출력하며 TypeError를 발생시킨다.

## 11.5 ABC 상속하기

collections.MutalbleSequence라는 ABC를 활용해서 FrenchDeck class를 다시 만들어보자.

```python
import collections

Card = collections.namedtuple('Card', ['rank', 'suit'])

class FrenchDeck2(collections.MutableSequence):
    ranks = [str(n) for n in range(2,11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()


    def __init__(self):
        self._cards = [Card(rank, suit) for suit in self.suits
                                        for rank in self.ranks]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]

    def __setitem__(self, position, value): # MutableSequence의 추상 메서드이다.
        self._cards[position] = value

    def __delitem__(self, position): # MutableSequence의 추상 메서드이다.
        del self._cards[position]

    def insert(self, position, value): # MutableSequence의 추상 메서드이다.
        self._cards.insert(position, value)
```

파이썬은 모듈을 로딩하거나 컴파일할 때가 아니라, 실행 도중 실세로 FrenchDeck2 객체를 생성할 때 추상 메서드의 구현 여부를 확인한다.

만약 추상 메서드가 구현되어 있지 않으면 TypeError 예외가 발생한다.

## 11.7 ABC의 정의와 사용

아래와 같은 상황을 만들어 본다고 가정하자.

> 웹사이트나 모바일 앱에서 광고를 무작위 순으로 보여주어야 하지만, 광고 목록에 들어 있는 광과를 모두 보여주기 전까지는 같은 광고를 반복하면 안 된다.

먼저 구현 해보자.

```python
import abc

class Tombola(abc.ABC):

    @abc.abstractmethod
    def load(self, iterable):
        """iterable의 항목들을 추가한다."""

    @abc.abstractmethod
    def pick(self):
        """
        무작위로 항목을 하나 제거하고 반환한다.
        객체가 비어 있을 때 이 메서드를 실행하면 'LookupError'가 발생한다.
        """

    def loaded(self):
        """
        최소 한 개의 항목이 있으면 True를, 아니면 False를 반한환다.
        """
        return bool(self.inspect())

    def inspect(self):
        """현재 안에 있는 항목들로 구성된 정렬된 튜플을 반환한다"""
        items = []
        while True:
            try:
                items.append(self.pick())
            except LookupError: # LookupError 예외는 파이썬 예외 계층구조에서 IndexError 및 KeyError와 관련 되어 있다.
                break
        self.load(items)
        return tuple(sorted(items))
```

테스트를 위해 추상 메서드를 구현하지 않으면서 상속 받고 객체를 생성하려고 하면 아래와 같은 에러를 출력한다

```python
>>> from tombola import Tombola
>>> class Fake(Tombola):
...     def pick(self):
...             return 13
...
>>> Fake
<class '__main__.Fake'>
>>> f = Fake()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: Can't instantiate abstract class Fake with abstract methods load
```

### 11.7.1 ABC 상세 구문

```python
class MyABC(abc.ABC):

    # 밑의 데코레이터 표현은 @abstractclassmethod와 같다. 하지만 파이썬 3.3 이후로 @abstractclassmethod 사용이 중단 되었다.
    # @abstractmethod와 def 사이에는 그 어느 것도 오면 안 된다는 것을 주의 하자
    @classmethod
    @abc.abstractmethod
    def bla(cls, ...):
        pass
```

### 11.7.2 Tombola ABC 상속하기

```python
import random

from tombola import Tombola

class LotteryBlower(Tombola):
    def __init__(self, iterable):
        self._balls = list(iterable)

    def load(self, iterable):
        self._balls.extend(iterable)

    def pick(self):
        try:
            position = random.randrange(len(self._balls))
        except ValueError:
            raise LookupError('pick from empty BingoCage')
        return self._balls.pop(position)

    def loaded(self):
        return bool(self._balls)

    def inspect(self):
        return tuple(sorted(self._balls))
```

여기서 `__init__()` 메서드를 살펴보자. self.\_balls는 list(iterable)로 저장된다.
이렇게 하면 어떠한 반복형이더라도 LotterBlower 클래스를 초기화할 수 있으므로 융통성이 향상된다.
이와 동시에 항목들을 리스트에 저장하므로 항목을 꺼낼 수 있도록 보장하고, list(iterable)을 실행하면 항상 인수의 사본이 생성되므로 인수로 받은 반복형에서 항목이 제거되도 전달 된 인수의 항목은 제거되지 않는다.

### 11.7.3 Tombola의 가상 서브 클래스

ABC의 register() 메서드는 호출하면 클래스가 등록된다. 등록된 클래스는 ABC의 가성 서브클래스가 되어 issubclass()와 isinstance() 함수에 의해 인식 되지만, **ABC에서 상속한 메서드나 속성은 전혀 없다.**

```python
>>> from tombola import Tombola
>>> from tombolist import TomboList
>>> issubclass(TomboList, Tombola)
True
>>> t = TomboList(range(100))
>>> isinstance(t, Tombola)
True
>>> TomboList.__mro__ # 상속을 운영하는 특별 클래스 속성 MRO(Method Resolution Order). 자기 자신과 자신의 슈퍼클래스들을 나열하는 결과를 보면 Tombola 클래스가 없는 것을 확인 할 수 있다. 상속하지 않는 것이다.
(<class 'tombolist.TomboList'>, <class 'list'>, <class 'object'>)
```

## 11.10 오리처럼 행동할 수 있는 거위

```python
>>> class Struggle:
...     def __len__(self): return 23
...
>>> from collections import abc
>>> isinstance(Struggle(), abc.Sized)
True
```

위의 예제에서 `__len__()` 메서드만 구현해도 abc.Sized의 서브클래스라고 간주되는 이유는 abc.Sized가 `__subclasshook__()`이라는 특별 클래스 메서드를 구현하기 때문이다.

```python
class Sized(metaclass=ABCMeta):
    __slots__ = ()

    @abstractmethod
    def __len__(self):
        return 0

    @classmethod
    def __subclasshook__(cls, C):
        if cls i Sized:
            if any("__len__" in B.__dict__ for B in C.__mro__): # c.__mro__에 나열된 클래스 중 __dict__ 속성에 __len__이라는 속성을 가진 클래스가 하나라도 있으면을 의미한다.
                return True

        return NotImplemented
```
