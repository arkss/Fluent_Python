# 15 콘텍스트 관리자와 else 블록

## 15.1 이것 다음에 저것: if 문 이외에서의 else 블록

if 문 이외에도 for, while, try에서도 else를 사용 할 수 있다.

- for : for 루프가 완전히 실행된 후에 else 블록이 실행
- while : 조건식이 거짓이 되어 while 루프를 빠져나온 후에 else 블록이 실행
- try : try 블록에서 예외가 발생하지 않을 때만 else 블록이 실행.

예외, return, break, continue 문이 복합문의 주요 블록을 빠져나오게 만들면 else 블록은 실행되지 않는다.

try/except 문의 예를 한 번 보자.

```python
try:
    dangerous_call()
    after_call()
except OSError:
    log('OSError..')
```

위의 코드에서 after_call은 dangerous_call에서 예외가 발생하지 않을 때만 실행 된다. 또한 after_call의 예외를 따로 처리하지 못 한다. else를 사용하면 이 코드를 좀 더 깔끔하게 바꿀 수 있다.

```python
try:
    dangerous_call()
except OSError:
    log('OSError..')
else:
    after_call()  # 이렇게 하면 after_call은 try 블록에서 예외가 발생하지 않는 경우에만 실행된다.
```

## 15.2 콘텍스트 관리자와 with 블록

콘텍스트 관리자 객체는 with 문을 제어하기 위해 존재한다.

with문은 try/finally 패턴(이 패턴은 예외, return, sys.exit() 호출 등의 이유로 어떤 블록의 실행이 중단되더라도 이후의 일정한 코드를 반드시 실행할 수 있게 보장)을 단순화하기 위해 설계되었다.

콘텍스트 관리자 프로토콜은 `__enter__()`와 `__exit__()` 메서드로 구성된다. with 문이 시작될 때 콘텍스트 관리자 객체의 `__enter__()` 메서드가 호출된다. `__enter__()`는 with 블록의 끝에서 finally 절의 역할을 수행한다.

```python
>>> with open('mirror.py') as fp:  # open() 함수가 TextIOWrapper 객체를 반환하고, 이 객체의 __enter__() 메서드는 self를 반환한다. 이때 as 절에 있는 타깃 변수의 값은 __enter__() 메서드의 결과이다.
...     src = fp.read(60)
...  # with 문을 빠져나오면 __enter__() 메서드가 반환한 객체가 아니라 콘텍스트 관리자 객체의 __exit__() 메서드가 호출된다.
>>> len(src)
60
>>> fp
<_io.TextIOWrapper name='mirror.py' mode='r' encoding='UTF-8'>
>>> fp.closed, fp.encoding
(True, 'UTF-8')
>>> fp.read(60)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: I/O operation on closed file.
```

아래 예는 콘텍스트 관리자와 `__enter__()` 메서드가 반환하는 객체의 차이를 보여준다

```python
class LookingGlass:

    def __enter__(self):
        import sys
        self.original_writer = sys.stdout.write
        sys.stdout.write = self.reverse_write
        return 'JABBERWOCKY'

    def reverse_write(self, text):
        self.original_writer(text[::-1])

    def __exit__(self, exc_type, exc_value, traceback):
        import sys
        sys.stdout.write = self.original_writer
        if exc_type is ZeroDivisionError:
            print('Please DO NOT divide by zero!')
            return True
```

```python
>>> from mirror import LookingGlass
>>> with LookingGlass() as what:  # LookingGlass 객체가 콘텍스트 관리자다. 콘텍스트 관리자의 __enter__() 메서드를 호출해서 반환된 값을 what에 바인딩한다.
...     print('Alice, Kitty and Snowdrop')
...     print(what)
...
pordwonS dna yttiK ,ecilA
YKCOWREBBAJ
>>> what
'JABBERWOCKY'
>>> print('Back to normal.')
Back to normal.
```

아래 코드는 with 문구 없이 LookingGlass 클래스를 사용하는 것을 보여준다.

```python
>>> from mirror import LookingGlass
>>> manager = LookingGlass()
>>> manager
<mirror.LookingGlass object at 0x107819490>
>>> monster = manager.__enter__()
>>> monster == 'JABBERWOCKY'
eurT
>>> monster
'YKCOWREBBAJ'
>>> manager
>094918701x0 ta tcejbo ssalGgnikooL.rorrim<
>>> manager.__exit__(None, None, None)
>>> monster
'JABBERWOCKY'
```

## 15.3 contextlib 유틸리티

contextlib 모듈에는 다양하게 응용할 수 있는 클래스와 함수가 있다.

이 유틸리티 중 @contextmanager 데커레이터에 대해 알아보도록 하자

## 15.4 @contextmanager 사용하기

@contextmanager는 `__enter__()` 메서드가 반환할 것을 생성하는 yield 문 하나를 가진 제너레이터만 구현하면 된다.

yield 문 앞에 있는 모든 코드는 with 블록 앞에서 인터프리터가 `__enter__()`를 호출할 때 실행되고, yield 문 뒤에 있는 코드는 블록의 마지막에서 `__exit__()`가 호출될 때 실행된다.

LookingGlass 클래스를 제너레이터 함수로 바꾼 예제를 보자

```python
import contextlib

@contextlib.contextmanager
def looking_glass():
    import sys
    original_write = sys.stdout.write

    def reverse_write(text):
        original_write(text[::-1])

    sys.stdout.write = reverse_write
    yield 'JABBERWOCKY'
    sys.stdout.write = original_write

>>> from mirror_gen import looking_glass
>>> with looking_glass() as what:
        print('Alice, kitty and snowdrop')
        print(what)
```

여기서 문제가 하나 있다. with 블록 안에서 예외가 발생하면 파이썬 인터프리터가 이 예외를 잡고, looking_glass() 안에 있는 yield 표현식에서 다시 예외를 발생시킨다. 그러나 예외 처리 코드가 없으므로 sys.stdout.write() 메서드를 복원하지 않고 중단 시켜서 시스템이 불안해진다.

예외처리를 하도록 하자

```python
import contextlib

@contextlib.contextmanager
def looking_glass():
    import sys
    original_write = sys.stdout.write

    def reverse_write(text):
        original_write(text[::-1])

    sys.stdout.write = reverse_write
    msg = ''
    try:
        yield 'JABBERWOCKY'
    except ZeroDivisionError:
        msg = 'Please DO NOT divide by zero!'
    finally:
        sys.stdout.write = original_write
        if msg:
            print(msg)
```

`__exit__()` 메서드는 예외 처리를 완료했음을 인터프리터에 알려주기 위해 True를 반환한다. True가 반환되면 인터프리터는 예외를 전파하지 않고 억제한다. 한편 `__exit__()`가 명시적으로 값을 반환하지 않으면 인터프리터는 예외를 전파한다.

@contextmanager 데커레이터를 사용하면 기본 작동이 반대로 된다.
데커레이터가 제공하는 `__exit__()` 메서드는 제너레이터에 전달된 예외가 모두 처리되었으므로 억제해야 한다고 생각한다. _억제하지 않게 하고 싶으면 데커레이트된 함수 안에서 명시적으로 예외를 다시 발생 시켜야 한다._
