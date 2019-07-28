# Simple container-based job scheduler

## Run Application

```
$ docker-compose up -d master
```

## API SPEC

0. 메인

```
$ curl http://0.0.0.0:5000
```

> You can find a list of jobs and api specs.

1. 작업 실행

```
$ curl http://0.0.0.0:5000/run/<service_name>
```
> http://0.0.0.0:5000/run/job_1

2. 작업 정지

```
$ curl http://0.0.0.0:5000/stop/<container_id>
```
> http://0.0.0.0:5000/stop/a8e8693e21fd

3. 작업 삭제

```
$ curl http://0.0.0.0:5000/remove/<container_id>
```
> http://0.0.0.0:5000/remove/a8e8693e21fd

4. 작업 스케일 in-out

```
$ curl http://0.0.0.0:5000/scale/<service_name>/<replicas>
```
> http://0.0.0.0:5000/scale/job_1/3

5. 작업 스케쥴링 상태 조회

```
$ curl http://0.0.0.0:5000/info
```

6. 자원 사용 현황 조회

```
$ curl http://0.0.0.0:5000/resource
```