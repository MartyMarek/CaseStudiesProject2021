# Using debian buster - alpine and slim did not work!
#FROM python:3.7-alpine #FROM python:slim
FROM python:3.7-buster

RUN mkdir /app
WORKDIR /app

ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD . /app/

EXPOSE 80

ENTRYPOINT [ "python" ]
CMD ["app.py"]