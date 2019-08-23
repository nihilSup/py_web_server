import threading
import queue


class QueueWorker(threading.Thread):

    def __init__(self, conn_queue):
        super().__init__(daemon=True)
        self.conn_queue = conn_queue
        self.enough = False

    def stop(self):
        self.enough = True

    def run(self):
        while not self.enough:
            try:
                task = self.conn_queue.get(timeout=1)
            except queue.Empty:
                continue
            try:
                task()
            except Exception:
                print('Unexpected error')
                continue
            finally:
                self.conn_queue.task_done()


class ThreadPool(object):

    def __init__(self, num_workers=10):
        self.num_workres = num_workers

    def __enter__(self):
        self.conn_queue = queue.Queue(self.num_workres * 5)
        self.workers = []
        for i in range(self.num_workres):
            t = QueueWorker(self.conn_queue)
            t.start()
            self.workers.append(t)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for worker in self.workers:
            worker.stop()
        for worker in self.workers:
            worker.join(timeout=30)
        return False if exc_type else True

    def submit(self, func, *args, **kwargs):
        self.conn_queue.put(lambda: func(*args, **kwargs))


class WorkerThread(threading.Thread):
    """
    Class to use in approach with server socket accept in worker:
    threads = []
            for _ in range(10):
                t = WorkerThread(s_socket, self.handle_client, daemon=True)
                t.start()
                threads.append(t)
            try:
                for t in threads:
                    t.join()
            except KeyboardInterrupt:
                pass

            for t in threads:
                t.stop()
            for t in threads:
                t.join()
    """

    def __init__(self, s_socket, handler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.socket = s_socket
        self.handler = handler
        self.enough = False

    def stop(self):
        self.enough = True

    def run(self):
        while not self.enough:
            try:
                c_socket, c_addr = self.socket.accept()
            except (OSError, ConnectionAbortedError):
                continue
            self.handler(c_socket, c_addr)


class DummyThreadPool(dummy.Pool):
    def submit(self, func, *args, **kwargs):
        return super().apply_async(func, args, kwargs)
