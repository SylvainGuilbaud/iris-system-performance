FROM python:3.9
WORKDIR /app

RUN apt-get update && \
    apt-get install -y locales && \
	sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales
    
ENV LC_ALL en_US.UTF-8 
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en   

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt


COPY . .
