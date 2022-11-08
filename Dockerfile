# docker build -f Dockerfile -t app:latest .

FROM ubuntu:20.04
RUN apt-get update && apt-get install --no-install-recommends -y python3.9 python3.9-dev python3-pip
EXPOSE 8501
EXPOSE 8000
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
COPY run.sh ./run.sh
RUN apt-get install -y dos2unix
RUN dos2unix ./run.sh
RUN chmod a+x run.sh
CMD ["sh","./run.sh"]