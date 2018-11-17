FROM python:3.6.7-stretch AS build

RUN mkdir /src
RUN mkdir /wheels

WORKDIR /src

COPY requirements.txt .

RUN pip wheel --no-cache-dir --wheel-dir /wheels -r /src/requirements.txt

COPY tg_dobby .
COPY setup.py .

RUN pip wheel --no-cache-dir --wheel-dir /wheels --no-index --find-links /wheels .

# TODO CONSIDER: Check ability to run on alpine
FROM python:3.6.7-slim-stretch

COPY --from=build /wheels /wheels

RUN pip install --no-index --find-links /wheels tg_dobby

ENV PYTHONUNBUFFERED 1

CMD python -m tg_dobby
