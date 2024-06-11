FROM python:3.11-alpine as builder


RUN apk update && \
  apk add g++=13.2.1_git20240309-r0 \
  make=4.4.1-r2 \
  cmake=3.29.3-r0 \
  gcc gfortran musl-dev libffi-dev=3.4.6-r0 git coreutils \
  py3-pyarrow=16.1.0-r0 \
  postgresql-dev \
  npm=10.8.0-r0

RUN --mount=type=cache,target=/root/.cache/pip \
  --mount=type=cache,target=/usr/local/lib/node_modules \
  python3 -m ensurepip --upgrade && \
  python3 -m pip install --no-cache-dir setuptools==70.0.0 && \
  python3 -m pip install --no-cache-dir poetry==1.8.3 && \
  npm -g install corepack

COPY pyproject.toml /docs-ai-scrap/pyproject.toml
COPY package.json .yarnrc.yml /docs-ai-scrap/
#COPY .yarn/ /docs-ai-scrap/.yarn/
COPY README.md /docs-ai-scrap/README.md
WORKDIR /docs-ai-scrap
RUN poetry install && \
  corepack enable && \
  yarn set version berry && \
  yarn install && yarn cache clean

COPY main.py store.js /docs-ai-scrap/
COPY deploy/* /docs-ai-scrap/deploy/

WORKDIR /docs-ai-scrap/deploy

ENTRYPOINT ["poetry", "run", "python", "main.py"]
#ENTRYPOINT [ "sleep", "100000" ]
