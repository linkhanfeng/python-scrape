ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}

# ENV HTTP_PROXY "http://127.0.0.1:50877"
# ENV HTTPS_PROXY "https://127.0.0.1:50877"

# 从 .env 文件中定义的变量
ARG TIME_ZONE
ARG PYTHON_VERSION
ARG CHANGE_SOURCE
ARG UBUNTU_SOURCE
ARG PYTHON_SOURCE_INDEX
ARG PYTHON_SOURCE_TRUSTED
ARG APP_CODE_PATH_CONTAINER

# 设置时区
RUN ln -snf /usr/share/zoneinfo/$TIME_ZONE /etc/localtime && echo $TIME_ZONE > /etc/timezone

## 更改 apt 源地址
# sed -i 's/原字符串/新字符串/' /path/to/file
RUN if [ ${CHANGE_SOURCE} = true ]; then \
    sed -i "s/deb.debian.org/${UBUNTU_SOURCE}/" /etc/apt/sources.list && \
    sed -i "s/security.debian.org/${UBUNTU_SOURCE}/" /etc/apt/sources.list && \
    sed -i "s/security-cdn.debian.org/${UBUNTU_SOURCE}/" /etc/apt/sources.list \
;fi

# WORKDIR /usr/src/app
# USER root
## 更改 pip 源
RUN mkdir -p ~/.pip
RUN if [ ${CHANGE_SOURCE} = true ]; then \
    echo "[global]\nindex-url=$PYTHON_SOURCE_INDEX\n[install]\ntrusted-host=$PYTHON_SOURCE_TRUSTED\n" >> ~/.pip/pip.conf \
;fi

# # 安装软件
# RUN apt-get update && apt-get install -yqq \
#     curl \
#     git \
#     zip \
#     unzip \
#     > /dev/null

# 安装 python 依赖
# WORKDIR ${APP_CODE_PATH_CONTAINER}
COPY ./requirements.txt /tmp/requirements.txt
RUN cd /tmp && pip install --no-cache-dir -r requirements.txt

# # Clean up
# RUN apt-get clean && \
#     rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
#     rm /var/log/lastlog /var/log/faillog
