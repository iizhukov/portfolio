FROM nginx:alpine

RUN apk add --no-cache gettext

COPY nginx.conf.template /etc/nginx/nginx.conf.template
COPY nginx.conf /etc/nginx/nginx.conf
COPY nginx.dev.conf /etc/nginx/nginx.dev.conf
COPY maintenance.html /usr/share/nginx/html/maintenance.html
COPY entrypoint.sh /docker-entrypoint.sh

RUN mkdir -p /etc/nginx/ssl && \
    chmod +x /docker-entrypoint.sh

EXPOSE 80 443

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health/nginx || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
