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

