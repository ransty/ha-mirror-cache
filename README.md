# ha-mirror-cache
PyPi mirroring without bandersnatch

```
docker compose -f docker-compose.yml build consumer webserver nginx
docker compose -f docker-compose.yml up -d
```

or...

# Create docker network for isolation
```
docker network create ha-mirror-cache
```

# Start Redis
```
docker run -d --name redis --hostname redis --network ha-mirror-cache redis
```

# Start consumer
```
docker run -d --name consumer --network ha-mirror-cache -v /path/to/cache:/opt/cache/ -v /path/to/simple:/opt/simple/ ransty/consumer
```

# Start webserver
```
docker run -d --name webserver -p 8080:80 --network ha-mirror-cache ransty/webserver
```

# Start nginx frontend
```
docker run -d --name nginx -p 80:80 --network ha-mirror-cache -v /path/to/cache:/usr/share/nginx/html/cache/ -v /path/to/simple:/usr/share/nginx/html/simple/ ransty/nginx
```
