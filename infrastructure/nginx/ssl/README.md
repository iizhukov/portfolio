# SSL Certificates

Эта директория должна содержать SSL сертификаты для HTTPS.

## Требуемые файлы

- `cert.pem` - SSL сертификат (может быть цепочка сертификатов)
- `key.pem` - приватный ключ сертификата

## Размещение файлов

Поместите ваши SSL сертификаты в эту директорию:

```
infrastructure/nginx/ssl/
├── cert.pem
└── key.pem
```

## Формат сертификатов

- `cert.pem` должен содержать сертификат в формате PEM
- `key.pem` должен содержать приватный ключ в формате PEM

## Пример для самоподписанного сертификата (только для разработки)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem \
  -out cert.pem \
  -subj "/C=RU/ST=State/L=City/O=Organization/CN=localhost"
```

**Внимание:** Самоподписанные сертификаты не подходят для production. Для production используйте сертификаты от доверенного CA (например, Let's Encrypt).

