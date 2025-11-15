#!/bin/sh
set -e

if [ -f /etc/nginx/nginx.conf.template ]; then
    echo "Generating nginx.conf from template..."
    envsubst '${NGINX_SERVER_NAME}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
    echo "nginx.conf generated successfully"
else
    echo "Using existing nginx.conf (no template found)"
fi

exec nginx -g "daemon off;"
