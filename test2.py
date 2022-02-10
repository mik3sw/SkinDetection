import threading
import time
import queue


q = queue.Queue()


def worker():
    while True:
        x = q.get()
        if x is None:
            break
        do_sth(x)
        q.task_done()


def do_sth(x):
    print(x)
    time.sleep(1)


threads = []
thread_count = 8

for x in range(0, thread_count):
    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()
    print('Started: %s' % t)

for x in range(0, 10):
    q.put(x)

# block until all tasks are done
q.join()

# stop workers
for _ in threads:
    q.put(None)

for t in threads:
    t.join()