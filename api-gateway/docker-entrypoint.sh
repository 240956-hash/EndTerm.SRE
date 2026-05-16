#!/bin/sh
set -e
DNS="$(awk '/^nameserver/{print $2; exit}' /etc/resolv.conf)"
if [ -n "${KUBERNETES_SERVICE_HOST:-}" ]; then
  NS="${POD_NAMESPACE:-default}"
  SUFFIX=".${NS}.svc.cluster.local"
else
  SUFFIX=""
fi

sed -e "s/__DNS__/${DNS}/" \
    -e "s/__FRONTEND_HOST__/frontend${SUFFIX}/" \
    -e "s/__AUTH_HOST__/auth-service${SUFFIX}/" \
    -e "s/__PRODUCT_HOST__/product-service${SUFFIX}/" \
    -e "s/__ORDER_HOST__/order-service${SUFFIX}/" \
    -e "s/__USER_HOST__/user-service${SUFFIX}/" \
    -e "s/__PAYMENT_HOST__/payment-service${SUFFIX}/" \
    -e "s/__NOTIFICATION_HOST__/notification-service${SUFFIX}/" \
  /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf
exec nginx -g 'daemon off;'
