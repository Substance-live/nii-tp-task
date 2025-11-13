FROM postgres:15-alpine

ENV POSTGRES_DB=documents_db
ENV POSTGRES_USER=postgres_admin
ENV POSTGRES_PASSWORD=postgres

EXPOSE 5432

