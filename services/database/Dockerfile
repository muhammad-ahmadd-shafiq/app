FROM postgres:16-alpine

# Scripts in this directory run once, when the data volume is first created.
COPY init.sql /docker-entrypoint-initdb.d/init.sql
