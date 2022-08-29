FROM python:3.10-alpine

RUN apk add --no-cache gcc musl-dev linux-headers

WORKDIR /code
COPY code .
RUN python3.10 -m pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 80

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
