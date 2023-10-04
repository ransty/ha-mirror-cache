# ha-mirror-cache
PyPi mirroring without bandersnatch

# Create docker network for isolation
docker network create ha-mirror-cache

# Start Redis
docker run -d --name redis --hostname redis --network ha-mirror-cache redis

# Start consumer
docker run -d --name consumer --network ha-mirror-cache -p 8000:8000 ransty/consumer

# Start webserver
docker run -d --namne webserver -p 8080:80 --network ha-mirror-cache ransty/webserver
