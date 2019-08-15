# Python web server implementation

## About

Web server implementation, based on ThreadedPoolExecutor. There is also branch with pool of processes with ThreadedPoolExecutor implementation. No usage of http parsing libs, no usage of HTTPBaseServer like libs

By default server serves static files from document root. It is also possible to add custom handlers to specific paths.

## How to use

```python
python -m web_server.httpd
```

minimal usecase, see Flags section below.

### Flags

* `-p, --port` and `-h, --host`, by default will listen to `localhost:8080`
* `-l, --log` log file path
* `-r`, `--root` to specify document root
* `-w`, `--workers` to specify number of workers in executors (if executor supports workers)
* `-v`, `--verbose` sets logging level to INFO (default ERROR)
* `-d`, `--debug` sets logging level to DEBUG

## How to test

```python
python -m unittest tests/integration/test_*.py
```

to run integration tests.

```python
python -m unittest tests/unit/test_*.py
```

to run unit tests.

## Warnings

* Current implementation supports only GET and HEAD methods.

* For integration tests server must be run by separate process and listen to port: 8080. Also httptest
dir must be present in document root. See <https://github.com/s-stupnikov/http-test-suite>

## TODO

* Add asyncio implementation
* Add POST, PUT support
* Add WSGI
* Improve performance

## Performance testing

### wr

```text
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
```

### ab

```text
Server Software:        otuserver
Server Hostname:        127.0.0.1
Server Port:            8080

Document Path:          /httptest/wikipedia_russia.html
Document Length:        954824 bytes

Concurrency Level:      100
Time taken for tests:   62.667 seconds
Complete requests:      50000
Failed requests:        16
   (Connect: 0, Receive: 0, Length: 16, Exceptions: 0)
Non-2xx responses:      16
Total transferred:      47737364141 bytes
HTML transferred:       47730213923 bytes
Requests per second:    797.87 [#/sec] (mean)
Time per request:       125.334 [ms] (mean)
Time per request:       1.253 [ms] (mean, across all concurrent requests)
Transfer rate:          743905.91 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0   58 297.6      0    7227
Processing:    -1   43 355.8     14   26786
Waiting:        0   24 355.1      3   26779
Total:          0  102 511.0     14   27853

Percentage of the requests served within a certain time (ms)
  50%     14
  66%     25
  75%     36
  80%     45
  90%     72
  95%    195
  98%   1127
  99%   1448
 100%  27853 (longest request)
 ```

### NB: ab tests were performed in CentOS docker image under MacOS

## References

<https://defn.io/tags/web-app-from-scratch/>
<https://dementiy.github.io/2017/11/22/08-async-server/>
