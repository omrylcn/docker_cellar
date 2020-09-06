FROM python:3.6-slim

RUN pip3 install numpy scikit-image

COPY ["/app","/app"]

WORKDIR "/app"

CMD ["python3","run.py"]




