FROM nginx:1.30

# конфиг копируется в образ, а не монтируется:
# так compose работает одинаково и локально, и из CI (через docker.sock)
COPY nginx.conf /etc/nginx/nginx.conf
