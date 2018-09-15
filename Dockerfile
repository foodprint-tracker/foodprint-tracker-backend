FROM python:3.6-slim

USER root
RUN groupadd -r app && useradd -r -m -g app app                                             

#===============
# System 
#===============
RUN apt-get update
RUN apt-get install --no-install-recommends -qqy python-pip python-setuptools python3-psycopg2
RUN apt-get install --no-install-recommends -qqy gcc python-dev 

#==================
# Python requirements
#==================
COPY ./requirements.txt /home/app/requirements.txt
RUN pip3.6 install -r /home/app/requirements.txt

#==================
# SRC Code
#==================
COPY . /home/app
RUN chown -R app /home/app
WORKDIR /home/app/src
CMD ["python3.6","manage.py", "runserver", "0.0.0.0:8000"]

EXPOSE 8000
