# 17 Future를 이용한 동시성

## 17.1 예제: 세 가지 스타일의 웹 내려받기

### 17.1.1 순차 내려받기 스크립트

아래는 순차적으로 국가 국기를 다운 받는 코드이다.

```python
import os
import time
import sys

import requests

POP20_CC = ('CN IN US ID BR PK NG BD RU JP '
            'MX PH VN ET EG DE IR TR CD FR').split()

BASE_URL = 'http://flupy.org/data/flags'

DEST_DIR = '/Users/maru/dev/book-study/Fluent_Python/Heejae/code/image'

def save_flag(img, filename):
    path = os.path.join(DEST_DIR, filename)
    with open(path, 'wb') as fp:
        fp.write(img)

def get_flag(cc):
    url = '{}/{cc}/{cc}.gif'.format(BASE_URL, cc=cc.lower())
    resp = requests.get(url)
    return resp.content

def show(text):
    print(text, end=' ')
    sys.stdout.flush()

def download_many(cc_list):
    for cc in sorted(cc_list):
        image = get_flag(cc)
        show(cc)
        save_flag(image, cc.lower() + '.gif')

    return len(cc_list)

def main(download_many):
    t0 = time.time()
    count = download_many(POP20_CC)
    elapsed = time.time() - t0
    msg = '\n{} flags downloaded in {:.2f}s'
    print(msg.format(count, elapsed))

if __name__ == '__main__':
    main(download_many)
```

### 17.1.2 concurrent.futures로 내려받기

concurrent.futures의 가장 큰 특징은 ThreadPoolExecutor와 ProcessPoolExecutor 클래스이다.

이 클래스들은 콜러블 객체를 서로 다른 스레드나 프로세스에서 실행할 수 있게 해주는 인터페이스를 구현한다. 그리고 작업자 스레드나 작업자 프로세스를 관리하는 풀과 실행할 작업을 담은 큐를 가지고 있다.

```python
from concurrent import futures

from flags import save_flag, get_flag, show, main

MAX_WORKERS = 20

def download_one(cc):
    image = get_flag(cc):
    show(cc)
    save_flag(image, cc.lower() + '.gif')
    return cc

def download_many(cc_list):
    workers = min(MAX_WORKERS, len(cc_list))
    # executor.__exit__() 메서드는 executor.shutdown(wait=True) 메서드를 호출하는데, 이 메서드는 모든 스레드가 완료될 때가지 블록된다.
    with futures.ThreadPoolExecutor(workers) as executor:
        res = executor.map(download_one, sorted(cc_list))

    # 스레드에서 호출한 함수 중 하나라도 발생하면, 암묵적으로 호출된 next()에서
    # 반복자의 해당 반환값을 가져올 때와 마찬가지로 여기에서 예외가 발생한다.
    return len(list(res))

if __name__ == '__main__':
    main(download_many)
```

### 17.1.3 Future는 어디에 있나?

파이썬 3.4 표준 라이브러리에서 Future라는 이름을 가진 클래스는 concurrent.futures.Future와 asyncio.Future다.

이 두 클래스의 객체는 완료되었을 수도 있고 아닐 수도 있는 지연된 계산을 표현하기 위해 사용된다.

Future 클래스는 자바스크립트 라이브러리의 Promise 객체와 비슷하다.

Future는 대기 중인 작업을 큐에 넣고, 완료 상태를 조사하고, 결과 (혹은 예외)를 가져올 수 있도록 캡슐화한다.

_Future는 개발자가 직접 객체를 생성하지 않고, `concurrent.futures`나 `asyncio` 같은 동시성 프레임워크에서만 배타적으로 생성해야 한다._ 왜냐하면 Future는 앞으로 일어날 일을 나타내고, Future의 실행을 스케줄링하는 프레임워크만이 어떤 일이 일어날지 확실히 알 수 있기 때문이다.

_클라이언트가 Future 객체의 상태를 직접 변경하면 안 된다._ Future 객체가 나타내는 연산이 완료되었을 때, 동시성 프레임워크가 Future 객체의 상태를 변경하기 때문이다. 그러므로 제어 할 수 없다.

두 프레임워크의 Future 클래스에는 논브로킹(?)이며 이 객체에 연결된 콜러블의 실행이 완료되었는지 여부를 불리언형으로 반환하는 `done()` 메서드가 있다. 일반적으로 클라이언트 코드는 Future가 완료되었는지 직접 물어보지 않고 통지해달라고 요청한다. 그렇기 때문에 Future 클래스에는 `add_done_callback()` 메서드가 있다.

두 프레임워크의 Future 클래스는 result() 메서드도 가지고 있는데, 완료된 경우 둘 다 콜러블의 결과를 반환하거나 콜러블이 실행될 때 발생한 예외를 다시 발생시킨다.

Future 객체를 보기 위해서 이전에 작성 했던 예제를 `futures.as_completed()`를 사용해서 고쳐보자.

```python
def download_many(cc_list):
    cc_list = cc_list[:5]
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        to_do = []
        for cc in sorted(cc_list):
            future = executor.submit(download_one, cc)
            to_do.append(future)
            msg = 'Scheduled for {}: {}'
            print(msg.format(cc, future))

        results = []
        # as_completed() 함수는 Future 객체를 담은 반복형을 인수로 받아,
        # 완료된 Future 객체를 생성하는 반복자를 반환한다.
        for future in futures.as_completed(to_do):
            res = futrue.result()
            msg = '{} result: {!r}'
            print(msg.format(future, res))
            results.append(res)

    return len(results)
```

엄격히 말하자면, 지금까지 테스트한 동시성 스크립트는 어느 것도 병렬로 내려 받을 수 없다. `concurrent.futures`는 전역 인터프리터 락(Global Interpreter Lock - GIL)에 의해 제한되며, flags_asyncio.py는 단일 스레드로 실행된다.

다음 절에서 `파이썬 스레드가 한 번에 한 스레드만 실행할 수 있게 해주는 GIL에 의해 제한된다면, 어떻게 flags_threadpool.py가 flags.py보다 5배나 빨리 실행될 수 있을까?`라는 의문증을 풀어보자

## 17.2 블로킹 I/O와 GIL

CPython 인터프리터는 내부적으로 스레드 안전하지 않으므로, 전역 인터프리터 락(GIL)을 가지고 있다. GIL은 한 번에 한 스레드만 파이썬 바이트코드를 실행하도록 제한한다. 그렇기 때문에 단일 파이썬 프로세스가 동시에 다중 CPU 코어를 사용할 수 없다.(이건 파이썬 언어적 특징이 아닌 CPython 인터프리터 특징이다.)

사실 C로 작성된 파이썬 라이브러리는 GIL을 관리하고, 자신의 OS 스레드를 생성해서 가용한 CPU코드를 모두 사용할 수 있다. 하지만 굉장히 복잡해진다.

그런데 **블로킹 입출력**(유저 프로세스가 커넬에 요청을 하면 결과가 나올 때까지 아무런 행동도 못하게 된다. 대기 시간 동안 다른 일을 하려면 추가로 자원을 사용하여 쓰레드를 생성해야 한다))을 실행하는 모든 표준 라이브러리 함수는 OS에서 결과를 기다리는 동안 GIL을 해제한다. 입출력 위주의 작업을 실행하는 파이썬 프로그램은 파이썬으로 구현하더라도 스레드를 이용함으로써 이득을 볼 수 있다. 파이썬 스레드가 네트워크로부터의 응답을 기다리는 동안, 블라킹된 입출력 함수가 GIL을 해제함으로써 다른 스레드가 실행될 수 있다.

## 17.3 concurrent.futures로 프로세스 실행하기

`concurrent.futures` 패키지는 ProcessPoolExecutor 클래스를 사용해서 작업을 여러 파이썬 프로세스에 분산시켜 진정한 병렬 컴퓨팅을 가능하게 한다.

ProcessPoolExecutor와 ThreadPoolExecutor는 모두 범용 Executor 인터페이스를 구현하므로, concurrent.futures를 사용하는 경우에는 스레드 기반의 프로그램을 프로세스 기반의 프로그램으로 쉽게 변환할 수 있다.

하지만 국기 예제 처럼 입출력 위주는 ProcessPoolExecutor를 사용해도 별 도움이 안된다.

```python
def download_many(cc_list):
    with futures.ProcessPoolExecutor() as executor:
        with futures.ProcessPoolExecutor() as executor:
```

ProcessPoolExecutor는 사용할 CPU 수를 선택적 인자로 받는다. 국기 예제 같은 경우, 국기 개수만큼의 CPU 수가 아니면 성능 떨어진다. 반면 스레드 같은 경우 필요에 따라 수천 개의 스레드를 사용할 수 있다. 그러므로 상황에 따라 스레드를 이용하는게 성능에 좋다.

반면 ProcessPoolExecutor는 계산 위주의 작업에서 진가를 발휘한다.

순수 파이썬으로 구현된 pypy 인터프리터의 경우 더 빨리진다. 계산 위주의 작업을 수행한다면 PyPy를 사용하는 것이 더 좋다.

## 17.4 Executor.map() 실험

```python
from time import sleep, strftime
from concurrent import futures


def display(*args):
    print(strftime('[%H:%M:%S]'), end=' ')
    print(*args)


def loiter(n):
    msg = '{}loiter({}): doing nothing for {}s...'
    display(msg.format('\t' * n, n, n))
    sleep(n)
    msg = '{}loiter({}): done.'
    display(msg.format('\t' * n, n))
    return n * 10


def main():
    display('Script starting.')
    executor = futures.ThreadPoolExecutor(max_workers=3)
    results = executor.map(loiter, range(5))  # map() 메서드는 논블로킹 메서드다.
    display('results:', results)
    display('Waiting for individual results:')

    # for 루프 안에서 enumerate()를 호출하면 암묵적으로 next(results)를 호출하는데, next(results)는 먼저 내부적으로 첫 번째 호출한 loiter(0)을 나타내는 Future 객체 _f의 result() 메서드를 호출한다. _f.result() 메서드는 _f가 완료될 때까지 블로킹 되므로, 다음번 결과가 나올 때까지 이 루프틑 블로킹 된다.
    for i, result in enumerate(results):
        display('result {}: {}'.format(i, result))


main()

```

Executor.map()은 호출한 순서 그대로 결과를 반환하는 특징이 있다. 첫 번째 호출이 결과를 생성할 때까지 10초 걸리고 나머지 호출은 1초씩 걸린다면, map()이 반환한 제너레이터가 첫 번째 결과를 가져오기까지 10초 걸린다. 그 후 다른 함수는 이미 실행을 완료했을 테니 나머지 결과는 바로 가져올 수 있다.

순서에 상관 없이 완료 됨에 따라 결과를 가져오려면 Executor.submit() 메서드와 futures.as_completed() 함수를 함께 사용하면 된다. 특히 submit은 다양한 콜러블과 인수를 제출 할 수 있어서 map보다 융통성이 높다.

## 17.5 진행 상황 출력하고 에러를 처리하며 내려받기

국가 국기를 다운 받는 예제를 좀 더 자세하게 만들었다. 책을 보며 구현해보자

### 17.5.3 스레드 및 멀티프로세스의 대안

futures.ThreadPoolExecutor로 처리하기 어려운 작업은 threading 모듈로 처리 할 수 있다.

계산 위주의 작업을 수행하는 경우에는 여러 프로세스를 실행해서 GIL을 피해나가야 한다.
futures.ProcessPoolExecutor를 사용하기 힘든 구조인 경우 multiprocessing 패키지를 사용하면 된다.
