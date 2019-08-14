import threading
import queue

import multiprocessing.queues as mp_queue
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process, cpu_count, Queue

import logging

log = logging.getLogger(__name__)


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


class ProcWorker(Process):

    def __init__(self, task_queue, num_thr=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_queue = task_queue
        self.num_thr = num_thr
        self.enough = False

    def stop(self):
        self.enough = True

    def run(self):
        with ThreadPoolExecutor(self.num_thr) as pool:
            while not self.enough:
                try:
                    task, args, kwargs = self.task_queue.get(timeout=1)
                except mp_queue.Empty:
                    continue
                try:
                    pool.submit(task, *args, **kwargs)
                except Exception as e:
                    log.exception(e)
                    continue


class ProcessPoolThreaded(object):
    def __init__(self, num_proc=None, num_thr=None):
        self.num_proc = num_proc or cpu_count()
        self.num_thr = num_thr or 10

    def __enter__(self):
        self.queue = Queue(self.num_proc * self.num_thr * 2)
        processes = []
        for _ in range(self.num_proc):
            p = ProcWorker(self.queue, self.num_thr)
            p.start()
            processes.append(p)
        self.processes = processes
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for p in self.processes:
            p.stop()
        for p in self.processes:
            p.join(timeout=30)
        return False if exc_type else True

    def submit(self, func, *args, **kwargs):
        self.queue.put((func, args, kwargs))
