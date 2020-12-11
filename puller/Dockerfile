FROM python:3.8-alpine AS builder
COPY requirements.txt requirements.txt
RUN apk --no-cache add gcc build-base
RUN pip install -U pip
RUN pip install --user -r requirements.txt

FROM python:3.8-alpine
COPY --from=builder /root/.local/bin /root/.local/bin
COPY --from=builder /root/.local/lib /root/.local/lib
COPY app.py /app.py

EXPOSE 8080
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "/app.py"]
