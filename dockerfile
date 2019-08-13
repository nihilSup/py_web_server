FROM centos/python-36-centos7
# FROM python:3.6
WORKDIR /web_server

COPY web_server /web_server/web_server
COPY tests /web_server/tests

EXPOSE 8080
CMD [ "python", "-m", "web_server.httpd", "-p", "8080", "--host", "0.0.0.0", "-w", "10"]
# CMD [ "ls", "-la"]
# CMD [ "bash"]