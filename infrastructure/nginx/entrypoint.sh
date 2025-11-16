#!/bin/sh

if [ -f /etc/nginx/ssl/cert.pem ] && [ -f /etc/nginx/ssl/key.pem ]; then
    USE_SSL=true
    echo "SSL certificates found, using HTTPS configuration"
else
    USE_SSL=false
    echo "SSL certificates not found, using HTTP-only configuration"
fi

if [ "$USE_SSL" = "false" ] && [ -f /etc/nginx/nginx.dev.conf ]; then
    echo "Using nginx.dev.conf (no SSL certificates)"
    if cp /etc/nginx/nginx.dev.conf /etc/nginx/nginx.conf 2>/dev/null; then
        echo "nginx.conf copied from nginx.dev.conf successfully"
    else
        echo "Warning: Could not write to /etc/nginx/nginx.conf (may be read-only mount)"
        echo "Using existing nginx.conf or default configuration"
    fi
elif [ -f /etc/nginx/nginx.conf.template ]; then
    echo "Generating nginx.conf from template..."
    
    NGINX_SERVER_NAME="${NGINX_SERVER_NAME:-_}"
    
    if [ "$NGINX_SERVER_NAME" = "_" ]; then
        sed -e 's/\${NGINX_SERVER_NAME:-_}/_/g' \
            /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf 2>/dev/null
    else
        SERVER_NAME_ESCAPED=$(echo "$NGINX_SERVER_NAME" | sed 's/[[\.*^$()+?{|]/\\&/g')
        sed -e "s/\${NGINX_SERVER_NAME:-_}/${SERVER_NAME_ESCAPED}/g" \
            /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf 2>/dev/null
    fi
    
    if [ $? -eq 0 ]; then
        echo "nginx.conf generated successfully"
    else
        echo "Warning: Could not write to /etc/nginx/nginx.conf (may be read-only mount)"
        echo "Using existing nginx.conf or default configuration"
    fi
else
    echo "Using existing nginx.conf (no template or dev config found)"
fi

exec nginx -g "daemon off;"
