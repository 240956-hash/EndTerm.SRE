FROM nginx:1.27-alpine
COPY api-gateway/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY api-gateway/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
EXPOSE 80
ENTRYPOINT ["/docker-entrypoint.sh"]
