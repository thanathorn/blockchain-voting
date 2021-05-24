import time
from multiprocessing import Process, Manager, Value

def foo(data, name=''):
    time.sleep(5)
    data.value += 5

if __name__ == "__main__":
    manager = Manager()
    x = manager.Value('i', -1)
    y = Value('i', 0)

    process = Process(target=foo, args=(x, 'x'))
    process.start()
    print( 'Before waiting: ')
    print( 'x = {0}'.format(x.value))
    process.terminate()
    while x.value == -1:
        pass
    print ('After waiting: ')
    print ('x = {0}'.format(x.value))