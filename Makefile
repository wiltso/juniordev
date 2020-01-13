.PHONY: up update-status docker-up build kill stop

up: update-status docker-up

update-status: 
	./updateStatuss.sh

docker-up: 
	docker-compose up -d

stop:
	docker-compose stop

kill:
	docker-compose kill

build:
	docker-compose build