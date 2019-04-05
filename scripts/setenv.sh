if [[ $# -eq 0 ]];then
  kcenv="LOCAL"
else
  kcenv=$1
fi

case "$kcenv" in
   IBMCLOUD)
        export KAFKA_BROKERS="kafka03-prod02.messagehub.services.us-south.bluemix.net:9093,kafka01-prod02.messagehub.services.us-south.bluemix.net:9093,kafka02-prod02.messagehub.services.us-south.bluemix.net:9093,kafka04-prod02.messagehub.services.us-south.bluemix.net:9093,kafka05-prod02.messagehub.services.us-south.bluemix.net:9093"
        export KAFKA_APIKEY="9WKzmHOGX6K6DwsNxKXBnrhijskOlMmDVdOgZdB8aTEzEJzJ"
        export KAFKA_ADMIN_URL= "https://kafka-admin-prod02.messagehub.services.us-south.bluemix.net:443"
        export KAFKA_ENV="IBMCLOUD"
        # export CA_LOCATION="/etc/ssl/certs"
        export CA_LOCATION="./Certificates.pem"
        ;;
   ICP)
        export KAFKA_BROKERS="172.16.50.228:30873"
        export KAFKA_ENV="ICP"
        export KAFKA_APIKEY="g8xaX5sRkF07ZegzqVnQYL7ObjIkrir90Xa3Iza6vXnA"
        export CA_LOCATION="es-cert.pem"
    ;;
   LOCAL)
        export KAFKA_BROKERS="kafka1:9092"
        export ORDER_CMD_MS="ordercmd:10080"
        export ORDER_QUERY_MS="orderquery:11080"
        export CONTAINER_MS="containerkstreams:12080"
   ;;
esac

echo $KAFKA_ENV
echo $KAFKA_BROKERS

