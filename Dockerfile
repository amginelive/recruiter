FROM python:slim
MAINTAINER Ilya Shupta <funn17@gmail.com>

ENV PYTHONUNBUFFERED=1 \
    NODE_ENV=production \
    DJANGO_SETTINGS_MODULE=conf.settings.prod \
    NGINX_VERSION=1.11.10-1~jessie \
    NPM_CONFIG_LOGLEVEL=info \
    NODE_VERSION=7.10.0

EXPOSE 80

## INSTALL NGINX
RUN echo "deb http://nginx.org/packages/mainline/debian/ jessie nginx" >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y curl ca-certificates gettext-base xz-utils \
    && curl http://nginx.org/keys/nginx_signing.key | apt-key add - \
    && apt-get update \
    && apt-get install -y nginx=${NGINX_VERSION} \
# forward request and error logs to docker log collector
    && ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log \
# Finished setting up Nginx
# Make NGINX run on the foreground
    && echo "daemon off;" >> /etc/nginx/nginx.conf \
# Remove default configuration from Nginx
    && rm /etc/nginx/conf.d/default.conf \
# And some custom paths, because why not
    && mkdir /recruiter \
    && mkdir /recruiter/var

## INSTALL NODE.JS
RUN set -ex \
  && for key in \
    9554F04D7259F04124DE6B476D5A82AC7E37093B \
    94AE36675C464D64BAFA68DD7434390BDBE9B9C5 \
    FD3A5288F042B6850C66B31F09FE44734EB7990E \
    71DCFD284A79C3B38668286BC97EC7A07EDE3FC1 \
    DD8F2338BAE7501E3DD5AC78C273792F7D83545D \
    B9AE9905FFD7803F25714661B63B535A4C206CA9 \
    C4F0DFFF4E8C1A8236409D08E73BC641CC11F4C8 \
    56730D5401028683275BD23C23EFEFE93C4CFFFE \
  ; do \
    gpg --keyserver ha.pool.sks-keyservers.net --recv-keys "$key" || \
    gpg --keyserver pgp.mit.edu --recv-keys "$key" || \
    gpg --keyserver keyserver.pgp.com --recv-keys "$key" ; \
  done

RUN curl -SLO "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.xz" \
  && curl -SLO "https://nodejs.org/dist/v$NODE_VERSION/SHASUMS256.txt.asc" \
  && gpg --batch --decrypt --output SHASUMS256.txt SHASUMS256.txt.asc \
  && grep " node-v$NODE_VERSION-linux-x64.tar.xz\$" SHASUMS256.txt | sha256sum -c - \
  && tar -xJf "node-v$NODE_VERSION-linux-x64.tar.xz" -C /usr/local --strip-components=1 \
  && rm "node-v$NODE_VERSION-linux-x64.tar.xz" SHASUMS256.txt.asc SHASUMS256.txt \
  && ln -s /usr/local/bin/node /usr/local/bin/nodejs

ADD var/requirements /recruiter/var/requirements

## INSTALL PROJECT REQUIREMENTS
RUN apt-get install -y $(grep -vE "^\s*#" /recruiter/var/requirements/requirements_deb.txt  | tr "\n" " ") && \
    ln -s /recruiter/var/supervisor-app.conf /etc/supervisor/conf.d/ && \
    pip install -r /recruiter/var/requirements/requirements_prod.txt

# Copy the modified Nginx conf
COPY var/nginx.conf /etc/nginx/conf.d/

ADD package.json /recruiter

WORKDIR /recruiter
RUN npm install

ADD . /recruiter

RUN python manage.py collectstatic -v0 --noinput && \
    npm run dist

CMD ["supervisord", "-n"]
