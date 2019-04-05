#!/usr/bin/env bash
kafkacat -C -b gc-kafka-0.gc-kafka-hl-svc.greencompute.svc.cluster.local:32224 -t text-topic
