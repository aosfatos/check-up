# builder
FROM docker.io/python:3.12.3 AS builder

RUN pip install --user pipenv

ENV PIPENV_VENV_IN_PROJECT=1

COPY Pipfile.lock Pipfile /usr/src/

WORKDIR /usr/src

RUN /root/.local/bin/pipenv sync --dev

RUN /usr/src/.venv/bin/python -c "import playwright; print(playwright)"

# runtime
FROM docker.io/python:3.12.3 AS runtime

COPY --from=builder /usr/src/.venv/ /usr/src/.venv/

RUN apt-get update \
    && rm -rf /var/lib/apt/lists/*

RUN /usr/src/.venv/bin/python -c "import playwright; print(playwright)"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /project

ENV PATH=/usr/src/.venv/bin:$PATH

# RUN groupadd -g 32767 herokuishuser \
#     && useradd -m -l herokuishuser -u 32767 -g 32767 \
#     && chown herokuishuser -R .

COPY . .

ENV PLAYWRIGHT_BROWSERS_PATH=/project/playwright
RUN playwright install --with-deps chromium

# USER herokuishuser

CMD ipython
