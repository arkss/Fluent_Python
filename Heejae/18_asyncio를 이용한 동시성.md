# 18 asyncio를 이용한 동시성

## 18.1 스레드와 코루틴 비교

threading 모듈의 스레드를 이용해서 구현한 spinner animate 예제와 asyncio 모듈의 코루틴을 이용해서 구현한 예제를 통해 다음과 같은 점을 알 수 있다.

- 스레드를 종료시키는 API는 정의되어 있지 않다. 스레드에 메세지를 보내 종료시켜야 한다.
- asyncio 코루틴 안에서 time.sleep()을 호출하지 말라. 주 스레드를 블로킹해서 이벤트 루프를 중단시키고 애플리케이션 전체가 멈추게 된다.

- asyncio.Task는 threading.Thread와 거의 대등하다.
- Task는 코루틴을 구동하고, Thread는 콜러블을 호출한다.
- Task 객체는 직접 생성하지 않고, 코루틴을 asyncio.async()나 loop.create_task()에 전달해서 가져온다.
- Task 객체를 가져오면, 이 객체는 이미 asyncio.async() 등에 의해 실행이 스케줄링되어 있다. Thread 객체는 start() 메서드를 호출해서 실행하라고 명령해야 한다.

### 18.1.1 asyncio.Future: 논블로킹 설계

asyncio.Future와 concurrent.futures.Future 클래스는 인터페이스가 거의 같지만 다르게 구현되어 있으므로 서로 바꿔 쓸 수 없다.

비슷한 부분을 보자

- asyncio에서 BaseEventLoop.create_task() 메서드는 코루틴을 받아서 실행하기 위해 스케줄링하고 asyncio.Task 객체를 반환한다. Task는 코루틴을 래핑하기 위해 설계된 Future의 서브클래스이므로, Task 객체는 Future 객체이기도 하다.이 과정은 Executor.submit()을 호출해서 concurrent.futures.Future 객체를 생성하는 방법과 비슷하다.
- concurrent.futures.Future의 result() 메서드는 asyncio.Future 클래스도 가지고 있지만, 아직 실행이 완료되지 않은 Future 객체의 result() 메서드를 호출하면, 결과를 기다리라 블로킹되는 대신 asyncio.InvalidStateError 예외가 발생한다. 대신 yield from을 호출하면 이벤트 루푸를 블로킹하지 않고 작업 완료를 기다리는 과정을 자동으로 처리해주므로 결과를 가져올 수 있다. 그러므로 add_done_callback()과 함수가 필요 없다.

### 18.1.2 Future, Task, 코루틴에서 생성하기

foo()가 코루틴 함수(호출되면 코루틴 객체를 반환한다)거나, Future나 Task 객체를 반환하는 일반 함수면, `res = yield from foo()` 코드가 작동한다. 이는 코루틴과 Future가 밀접한 관계임을 의미한다.

## 18.2 asyncio와 aiohttp로 내려받기

asyncio.wait() 코루틴은 Future 객체나 코루틴의 반복형을 받고, wait()는 각 코루틴을 Task 안에 래핑한다. 결국 wait()가 관리하는 모든 객체는 Future 객체가 된다. 그리고 이 함수는 코루틴 함수이기 때문에 이를 호출하면 코루틴/제너레이터 객체가 반환된다.

loop.run_until_complete() 함수는 Future 객체나 코루틴을 받는다. 코루틴을 받으면 wait()가 하는 것과 비슷하게 run_until_complete()도 코루틴을 Task 안에 래핑한다.

yield from foo 구문을 사용하면 현재의 코루틴(즉, yield from 코드가 있는 대표 제너레이터)이 중단되지만, 제어권이 이벤트 루프로 넘어가고 이벤트 루프가 다른 코루틴을 구동 할 수 있게 되므로, 블로킹되지 않는다.

## 18.3 블로킹 호출을 에둘러 실행하기

이제 앞서 말했던 질문의 해답을 찾아보자

**둘 다 단일 스레드로 실행되는데, 어떻게 flags_asnycio.py가 flags.py보다 5배나 빨리 실행될까?**

라이언 달(노드js 창시자)은 블로킹 함수를 디스크나 네트워크 입출력의 수행으로 정의한다.

블로킹 함수가 전체 애플리케이션의 실행을 멈추지 않게 하는 두 가지 방법이 있다.

- 블로킹 연산을 각기 별도의 스레드에서 실행한다.
- 모든 블로킹 연산을 논블로킹 비동기 연산으로 바꾼다.

파이썬이 사용하는 OS 스레드는 (OS에 따라 다르지만) 각기 수메가바이트의 메모리를 사용한다. 수천 개의 연결을 처리해야 한다면 연결마다 하나의 스레드를 사용할 수 없다.

전통적으로 메모리 부담을 줄이기 위해 콜백으로 비동기 호출을 구현한다. 응답을 기다리지 않고, 어떤 일이 발생할 때 호출될 함수를 등록한다. 이렇게 호출한 것을 논블로킹으로 만든다.

코루틴으로 사용될 때 제너레이터는 비동기 프로그래밍을 할 수 있는 대안을 제시한다. 이벤트 루프의 관점에서 보면, 콜백을 호출하는 작업이나 중단된 코루틴의 send() 메서드를 호출하는 작업은 거의 같다.
