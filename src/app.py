import multiprocessing
import math
import json


def sieve_segment(start, end, conn):
    """Aplica la criba en un segmento de números desde start hasta end."""
    sieve = [True] * (end - start)
    for i in range(2, int(math.sqrt(end)) + 1):
        for j in range(max(i * i, ((start + i - 1) // i) * i), end, i):
            sieve[j - start] = False
    primes = [num for idx, num in enumerate(range(start, end)) if sieve[idx] and num >= 2]
    conn.send(primes)
    conn.close()

def parallel_sieve(n, num_processes):
    """Implementación paralela de la Criba de Eratóstenes."""
    segment_size = n // num_processes
    processes = []
    parent_conns = []

    for i in range(num_processes):
        start = i * segment_size
        end = n if i == num_processes - 1 else (i + 1) * segment_size
        parent_conn, child_conn = multiprocessing.Pipe()
        p = multiprocessing.Process(target=sieve_segment, args=(start, end, child_conn))
        processes.append(p)
        parent_conns.append(parent_conn)
        p.start()

    primes = []
    for conn in parent_conns:
        primes.extend(conn.recv())

    for p in processes:
        p.join()

    return sorted(primes)


def lambda_handler(event, context):
    n = event['n']
    num_processes = event['process']
    primes = parallel_sieve(n, num_processes)
    print(primes)
    return {
        'statusCode': 200,
        'body': json.dumps(primes)
    }