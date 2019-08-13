# About:
Web server implementation. No usage of http parsing libs, no usage of HTTPBaseServer like libs

By default server serves static files from document root. It is also possible to add custom handlers to specific paths.

# How to use:
```python -m web_server.httpd```

## Flags: 
* `-p, --port` and `-h, --host`
* `-l, --log` for log file path
* `-r`, `--root` to specify document root
* `-w`, `--workers` to specify number of workers in executors (if executor supports workers)

# Warning:
Current implementation supports only GET and HEAD methods.

# How to test:
```python -m unittest tests/integration/test_*.py``` to run integration tests.
## Warning:
For integration tests server must be run by separate process and listen to port: 8080. Also httptest dir must be present in document root. See https://github.com/s-stupnikov/http-test-suite
```python -m unittest tests/unit/test_*.py``` to run unit tests.
