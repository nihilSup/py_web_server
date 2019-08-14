FROM centos/python-36-centos7

WORKDIR /web_server

COPY web_server /web_server/web_server
COPY tests /web_server/tests

EXPOSE 8080
CMD [ "python", "-m", "web_server.httpd", "-p", "8080", "--host", "0.0.0.0", "-w", "10"]