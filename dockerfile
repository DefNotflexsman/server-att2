FROM python:3.11-slim
RUN apt-get update && apt-get install -y git nodejs npm supervisor
WORKDIR /app
COPY . .
RUN git clone https://github.com/UseInterstellar/Interstellar.git /app/interstellar
RUN cd /app/interstellar && npm install
RUN pip install -r requirements.txt
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]