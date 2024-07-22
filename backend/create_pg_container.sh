#!/bin/bash
docker run --name residency_hackathon \
  -p$PG_PORT:5432 \
  -e POSTGRES_USER=$PG_USER \
  -e POSTGRES_PASSWORD=$PG_PASSWORD \
  -e POSTGRES_DB=$PG_DB \
  -d \
  ankane/pgvector \
;
