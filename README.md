# ha-mirror-cache
PyPi mirroring without bandersnatch

```
docker compose build consumer webserver nginx
docker compose up -d
```

or...

## Create docker network for isolation
```
docker network create ha-mirror-cache
```

## Start Redis
```
docker run -d --name redis --hostname redis --network ha-mirror-cache redis
```

## Start consumer
```
docker run -d --name consumer --network ha-mirror-cache -v /path/to/cache:/opt/cache/ -v /path/to/simple:/opt/simple/ ransty/consumer
```

## Start webserver
```
docker run -d --name webserver -p 8080:80 --network ha-mirror-cache ransty/webserver
```

## Start nginx frontend
```
docker run -d --name nginx -p 80:80 --network ha-mirror-cache -v /path/to/cache:/usr/share/nginx/html/cache/ -v /path/to/simple:/usr/share/nginx/html/simple/ ransty/nginx
```


# Mirror something!
```
$ curl -i -X POST -H 'Content-Type: application/json' -d '{"package": "pika", "version": "1.0.0"}' localhost:8080

webserver  | INFO:root:Starting httpd...
webserver  | 
webserver  | 
consumer   | INFO:root:Waiting for messages on cache stream
webserver  | INFO:root:User requested package pika latest
consumer   | INFO:root:Downloading package pika
webserver  | 10.10.5.1 - - [04/Oct/2023 10:54:09] "POST / HTTP/1.1" 200 -
consumer   | Collecting pika
consumer   |   Downloading pika-1.3.2-py3-none-any.whl (155 kB)
consumer   |      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 155.4/155.4 kB 2.6 MB/s eta 0:00:00
consumer   | 
consumer   | 
consumer   | Saved /opt/cache/pika-1.3.2-py3-none-any.whl
consumer   | Successfully downloaded pika
consumer   | INFO:root:Re-indexing simple
```


