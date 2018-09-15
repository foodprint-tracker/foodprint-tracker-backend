all: build run

build:
	docker build -t food .
run: 
	docker run --rm -ti -v ${PWD}/local_settings.py:/home/app/src/base/local_settings.py -p 8000:8000 food $(filter-out $@,$(MAKECMDGOALS))
