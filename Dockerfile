# ubuntu LTS version
FROM ubuntu:22.04 AS builder-image

# avoid stuck build due to user prompt
ARG DEBIAN_FRONTEND=noninteractive
ARG VENV_PATH=/home/iasyc/venv

RUN apt update && apt install --no-install-recommends -y python3.10 python3.10-dev python3.10-venv python3-pip python3-wheel build-essential && \
    apt clean && rm -rf /var/lib/apt/lists/*

# create and activate virtual environment
# using final folder name to avoid path issues with packages
RUN python3.10 -m venv /home/iasyc/venv
ENV PATH="$VENV_PATH/bin:$PATH"

# install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir wheel
RUN pip install --no-cache-dir -r requirements.txt

# runner image
FROM ubuntu:22.04 AS runner-image

ARG VENV_PATH=/home/iasyc/venv
ARG WORK_DIR=/home/iasyc/eco_rutas_procesos

RUN apt update && apt install --no-install-recommends -y python3.10 python3.10-venv tzdata && \
    apt clean && rm -rf /var/lib/apt/lists/*

# set correct timezone
RUN ln -fs /usr/share/zoneinfo/America/Bogota /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

RUN useradd --create-home iasyc
COPY --from=builder-image $VENV_PATH $VENV_PATH

# activate virtual environment
ENV VIRTUAL_ENV=$VENV_PATH
ENV PATH="$PATH:$VENV_PATH/bin:$WORK_DIR/api"
RUN echo $PATH

USER iasyc
WORKDIR $WORK_DIR
COPY --chown=1000:1000 . .
WORKDIR "$WORK_DIR/api"

# launch api
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--log-config", "./logging.conf"]
