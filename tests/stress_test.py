import threading
import time
import requests
import random
import json

BASE_URL = 'http://127.0.0.1:5001'
CONCURRENT_REQUESTS = 100
TOTAL_REQUESTS = 500

success_count = 0
fail_count = 0
lock = threading.Lock()
start_time = None


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
            timeout=10
        )
        result = response.json()
        with lock:
            if result.get('code') == 200:
                success_count += 1
            else:
                fail_count += 1
                print(f'[Thread {thread_id}] Failed: {result.get("message")}')
    except Exception as e:
        with lock:
            fail_count += 1
            print(f'[Thread {thread_id}] Exception: {str(e)}')


def worker(thread_id):
    plates = [f'京TEST{str(i).zfill(4)}' for i in range(CONCURRENT_REQUESTS)]
    for i in range(TOTAL_REQUESTS // CONCURRENT_REQUESTS):
        plate = plates[(thread_id + i) % len(plates)]
        direction = 'in' if i % 2 == 0 else 'out'
        send_gate_upload(thread_id, plate, direction)
        time.sleep(random.uniform(0.01, 0.05))


def main():
    global start_time
    start_time = time.time()

    print(f'开始并发测试：{CONCURRENT_REQUESTS} 个并发线程，共 {TOTAL_REQUESTS} 次请求')

    threads = []
    for i in range(CONCURRENT_REQUESTS):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    elapsed = time.time() - start_time
    print(f'\n========== 测试结果 ==========')
    print(f'总耗时: {elapsed:.2f} 秒')
    print(f'成功: {success_count}')
    print(f'失败: {fail_count}')
    print(f'成功率: {(success_count / (success_count + fail_count) * 100):.2f}%')
    print(f'QPS: {(success_count + fail_count) / elapsed:.2f}')

    if fail_count == 0:
        print('\n✅ 所有请求处理成功，连接泄漏问题已修复！')
    else:
        print(f'\n❌ 仍有 {fail_count} 个请求失败，需要进一步排查')


if __name__ == '__main__':
    main()
