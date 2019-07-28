# Simple container-based job scheduler

## Run Application

```
$ docker-compose up -d
```

## API SPEC

1. 작업 실행
```
http://0.0.0.0:5000/run/<image_name>
```

2. 작업 정지
```
http://0.0.0.0:5000/stop/<container_id>
```

3. 작업 삭제
```
http://0.0.0.0:5000/remove/<container_id>
```

4. 작업 스케일 in-out
```
http://0.0.0.0:5000/scale/<container_id>/<replicas>
```

5. 작업 스케쥴링 상태 조회
```
http://0.0.0.0:5000/info
```

6. 자원 사용 현황 조회
```
http://0.0.0.0:5000/resource
```