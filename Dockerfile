FROM python:slim
MAINTAINER Ilya Shupta <funn17@gmail.com>

ENV PYTHONUNBUFFERED=1 \
    NODE_ENV=production \
    DJANGO_SETTINGS_MODULE=conf.settings.prod \
    NGINX_VERSION=1.11.10-1~jessie

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

ADD var/requirements /recruiter/var/requirements

## INSTALL PROJECT REQUIREMENTS
RUN apt-get install -y $(grep -vE "^\s*#" /recruiter/var/requirements/requirements_deb.txt  | tr "\n" " ") && \
    ln -s /recruiter/var/supervisor-app.conf /etc/supervisor/conf.d/ && \
    pip install -r /recruiter/var/requirements/requirements_prod.txt

# Copy the modified Nginx conf
COPY var/nginx.conf /etc/nginx/conf.d/

WORKDIR /recruiter

ADD . /recruiter

RUN python manage.py collectstatic -v0 --noinput

CMD ["supervisord", "-n"]
