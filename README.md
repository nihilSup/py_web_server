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

# Performance testing
## wrk:
Running 10s test @ http://127.0.0.1:8080/httptest/dir2
  12 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    11.05ms   38.68ms 636.46ms   98.29%
    Req/Sec   170.15    129.59     0.95k    68.18%
  15499 requests in 10.06s, 2.56MB read
  Socket errors: connect 0, read 757, write 23, timeout 0
Requests/sec:   1540.82
Transfer/sec:    260.34KB

Running 1m test @ http://127.0.0.1:8080/httptest/dir2
  12 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     7.39ms   13.06ms 357.79ms   99.38%
    Req/Sec   163.24    119.46   616.00     66.88%
  21619 requests in 1.00m, 3.57MB read
  Socket errors: connect 50, read 733, write 49, timeout 0
Requests/sec:    359.69
Transfer/sec:     60.77KB

