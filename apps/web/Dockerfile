FROM node:25-alpine AS builder

WORKDIR /app

ENV NODE_OPTIONS="--max-old-space-size=1536"
ENV NODE_ENV=production
ENV CI=true

COPY package.json yarn.lock ./

RUN yarn install --frozen-lockfile --network-timeout 100000 --production=false && \
    yarn cache clean && \
    rm -rf /tmp/* && \
    rm -rf /var/cache/apk/* && \
    apk cache clean || true

COPY . .

RUN NODE_OPTIONS="--max-old-space-size=1536" yarn tsc -b --incremental false && \
    sync && \
    NODE_OPTIONS="--max-old-space-size=1536" yarn vite build && \
    rm -rf node_modules && \
    rm -rf .yarn && \
    rm -rf src && \
    rm -rf public && \
    rm -rf .vite && \
    rm -rf .cache && \
    rm -f tsconfig*.json vite.config.ts tailwind.config.ts postcss.config.ts eslint.config.js package.json yarn.lock && \
    rm -rf /tmp/* && \
    rm -rf /var/cache/apk/*

FROM nginx:alpine AS production

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
