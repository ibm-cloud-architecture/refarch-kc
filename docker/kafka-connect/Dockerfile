FROM  ibmcom/eventstreams-kafka-ce-icp-linux-amd64:2019.4.1-095ae1e as builder

FROM ibmjava:8-jre

RUN addgroup --gid 5000 --system esgroup && \
    adduser --uid 5000 --ingroup esgroup --system esuser

COPY --chown=esuser:esgroup --from=builder /opt/kafka/bin/ /opt/kafka/bin/
COPY --chown=esuser:esgroup --from=builder /opt/kafka/libs/ /opt/kafka/libs/
COPY --chown=esuser:esgroup --from=builder /opt/kafka/config/connect-distributed.properties /opt/kafka/config/
COPY --chown=esuser:esgroup --from=builder /opt/kafka/config/connect-log4j.properties /opt/kafka/config/
RUN mkdir /opt/kafka/logs && chown esuser:esgroup /opt/kafka/logs

RUN mkdir /opt/connectors && chown esuser:esgroup /opt/connectors
COPY --chown=esuser:esgroup connectors /opt/connectors/
COPY --chown=esuser:esgroup es-cert.jks /opt/kafka/

WORKDIR /opt/kafka

EXPOSE 8083

USER esuser

ENTRYPOINT ["./bin/connect-distributed.sh", "config/connect-distributed.properties"]
