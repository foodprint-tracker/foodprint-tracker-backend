all: build run

build:
	docker build -t food .
run: 
	docker run --rm --net=host -ti -v ${PWD}/local_settings.py:/home/app/src/base/local_settings.py food $(filter-out $@,$(MAKECMDGOALS))
