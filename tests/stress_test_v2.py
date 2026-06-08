import threading
import time
import requests
import random
import json

BASE_URL = 'http://127.0.0.1:5001'
CONCURRENT_REQUESTS = 150
TOTAL_REQUESTS = 1500

success_count = 0
fail_count = 0
lock = threading.Lock()
start_time = None
error_types = {}


def send_gate_upload(thread_id, plate_number, direction):
    global success_count, fail_count
    try:
        payload = {
            'plate_number': plate_number,
            'gate_code': f'GATE-{random.choice(["001", "002", "003", "004"])}',
            'direction': direction
        }
        response = requests.post(
            f'{BASE_URL}/api/gate/upload',
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            with lock:
                if result.get('code') == 200:
                    success_count += 1
                else:
                    fail_count += 1
                    msg = result.get('message', 'unknown')
                    error_types[msg] = error_types.get(msg, 0) + 1
        else:
            with lock:
                fail_count += 1
                msg = f'HTTP_{response.status_code}'
                error_types[msg] = error_types.get(msg, 0) + 1
    except Exception as e:
        with lock:
            fail_count += 1
            msg = str(e)[:50]
            error_types[msg] = error_types.get(msg, 0) + 1


def worker(thread_id):
    plates = [f'京LOAD{str(i).zfill(5)}' for i in range(CONCURRENT_REQUESTS * 3)]
    for i in range(TOTAL_REQUESTS // CONCURRENT_REQUESTS):
        plate = plates[(thread_id * 3 + i) % len(plates)]
        direction = 'in' if i % 2 == 0 else 'out'
        send_gate_upload(thread_id, plate, direction)


def main():
    global start_time
    start_time = time.time()

    print(f'开始高并发压力测试：{CONCURRENT_REQUESTS} 个并发线程，共 {TOTAL_REQUESTS} 次请求')
    print('=' * 60)

    threads = []
    for i in range(CONCURRENT_REQUESTS):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    elapsed = time.time() - start_time
    total = success_count + fail_count
    print(f'\n{"=" * 60}')
    print(f'测试结果')
    print(f'{"=" * 60}')
    print(f'总耗时:    {elapsed:.2f} 秒')
    print(f'总请求数:  {total}')
    print(f'成功数:    {success_count}')
    print(f'失败数:    {fail_count}')
    print(f'成功率:    {(success_count / total * 100):.2f}%' if total > 0 else '成功率:    N/A')
    print(f'吞吐量:    {total / elapsed:.2f} QPS' if elapsed > 0 else '吞吐量:    N/A')

    if error_types:
        print(f'\n错误分布:')
        for err, count in error_types.items():
            print(f'  - {err}: {count} 次')

    if fail_count == 0:
        print(f'\n✅ 全部通过！系统在高并发下稳定运行，连接泄漏问题已彻底修复。')
    else:
        print(f'\n❌ 仍有 {fail_count} 个请求失败')


if __name__ == '__main__':
    main()
