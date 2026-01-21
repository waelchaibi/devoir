FROM nginx:alpine

COPY frontend/src/index.html /usr/share/nginx/html/
COPY frontend/src/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
