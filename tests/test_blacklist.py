import json
import urllib.request

BASE_URL = 'http://127.0.0.1:5001'

def post(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def get(url):
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode('utf-8'))

def test_1_blacklist_check():
    print('=' * 60)
    print('测试 1: 黑名单检查')
    print('=' * 60)

    print('\n1.1 张三（京A12345）- 有逾期，应被拦截')
    result = post(f'{BASE_URL}/api/blacklist/check', {'plate_number': '京A12345'})
    data = result['data']
    assert data['is_blacklisted'] == True, '张三应该在黑名单中'
    assert data['intercept_flag'] == True, '拦截标记应为 True'
    assert data['overdue_bill_count'] >= 3, '逾期账单应 >= 3'
    print(f'  ✓ 黑名单状态: {data["is_blacklisted"]}')
    print(f'  ✓ 拦截标记: {data["intercept_flag"]}')
    print(f'  ✓ 逾期账单数: {data["overdue_bill_count"]}')
    print(f'  ✓ 欠费总额: {data["total_outstanding"]}')

    print('\n1.2 李四（京B67890）- 无逾期，不拦截')
    result = post(f'{BASE_URL}/api/blacklist/check', {'plate_number': '京B67890'})
    data = result['data']
    assert data['is_blacklisted'] == False, '李四不应该在黑名单中'
    assert data['intercept_flag'] == False, '拦截标记应为 False'
    print(f'  ✓ 黑名单状态: {data["is_blacklisted"]}')
    print(f'  ✓ 拦截标记: {data["intercept_flag"]}')

def test_2_gate_upload():
    print('\n' + '=' * 60)
    print('测试 2: 车闸上报接口')
    print('=' * 60)

    print('\n2.1 黑名单车辆（京A12345）出场 - 应返回拦截标记')
    result = post(f'{BASE_URL}/api/gate/upload', {
        'plate_number': '京A12345',
        'gate_code': 'GATE-002',
        'direction': 'out'
    })
    data = result['data']
    assert data['intercept_flag'] == True, '出场时应有拦截标记'
    assert data['intercept_reason'] is not None, '应有拦截原因'
    print(f'  ✓ 消息: {result["message"]}')
    print(f'  ✓ 拦截标记: {data["intercept_flag"]}')
    print(f'  ✓ 拦截原因: {data["intercept_reason"][:30]}...')

    print('\n2.2 正常车辆（京B67890）出场 - 不拦截')
    result = post(f'{BASE_URL}/api/gate/upload', {
        'plate_number': '京B67890',
        'gate_code': 'GATE-002',
        'direction': 'out'
    })
    data = result['data']
    assert data['intercept_flag'] == False, '正常车辆不应被拦截'
    print(f'  ✓ 消息: {result["message"]}')
    print(f'  ✓ 拦截标记: {data["intercept_flag"]}')

    print('\n2.3 外来车辆（京TEST001）入场+出场 - 不拦截')
    post(f'{BASE_URL}/api/gate/upload', {
        'plate_number': '京TEST001',
        'gate_code': 'GATE-001',
        'direction': 'in'
    })
    result = post(f'{BASE_URL}/api/gate/upload', {
        'plate_number': '京TEST001',
        'gate_code': 'GATE-002',
        'direction': 'out'
    })
    data = result['data']
    assert data['intercept_flag'] == False, '外来车辆不应被拦截'
    print(f'  ✓ 消息: {result["message"]}')
    print(f'  ✓ 拦截标记: {data["intercept_flag"]}')

def test_3_billing_calculate():
    print('\n' + '=' * 60)
    print('测试 3: 停车费计算接口（含拦截信息）')
    print('=' * 60)

    post(f'{BASE_URL}/api/gate/upload', {
        'plate_number': '京A12345',
        'gate_code': 'GATE-001',
        'direction': 'in',
        'record_time': '2026-06-08 10:00:00'
    })

    print('\n3.1 黑名单车辆计费 - 应包含拦截信息')
    result = post(f'{BASE_URL}/api/billing/calculate', {
        'plate_number': '京A12345',
        'exit_time': '2026-06-08 14:30:00'
    })
    data = result['data']
    assert data['intercept_flag'] == True, '计费结果应有拦截标记'
    assert 'intercept_reason' in data, '应有拦截原因'
    assert 'overdue_bills' in data, '应有逾期账单列表'
    print(f'  ✓ 停车费: {data["parking_amount"]} 元')
    print(f'  ✓ 拦截标记: {data["intercept_flag"]}')
    print(f'  ✓ 拦截原因: {data["intercept_reason"][:30]}...')
    print(f'  ✓ 逾期账单数: {data["overdue_bill_count"]}')
    print(f'  ✓ 欠费总额: {data["total_outstanding"]} 元')

def test_4_intercept_records():
    print('\n' + '=' * 60)
    print('测试 4: 拦截记录查询')
    print('=' * 60)

    result = get(f'{BASE_URL}/api/blacklist/intercepts')
    data = result['data']
    assert len(data) > 0, '应该有拦截记录'
    print(f'  ✓ 拦截记录数: {len(data)}')
    print(f'  ✓ 最新拦截: {data[0]["plate_number"]} - {data[0]["intercept_reason"][:20]}...')

def test_5_property_bill_summary():
    print('\n' + '=' * 60)
    print('测试 5: 物业费欠费汇总')
    print('=' * 60)

    result = get(f'{BASE_URL}/api/property-bill/summary?plate_number=京A12345')
    data = result['data']
    assert data['is_blacklisted'] == True
    print(f'  ✓ 车牌号: {data["plate_number"]}')
    print(f'  ✓ 欠费总额: {data["total_outstanding"]} 元')
    print(f'  ✓ 未缴账单数: {data["unpaid_bill_count"]}')
    print(f'  ✓ 逾期账单数: {data["overdue_bill_count"]}')
    print(f'  ✓ 是否黑名单: {data["is_blacklisted"]}')

if __name__ == '__main__':
    try:
        test_1_blacklist_check()
        test_2_gate_upload()
        test_3_billing_calculate()
        test_4_intercept_records()
        test_5_property_bill_summary()

        print('\n' + '=' * 60)
        print('✅ 所有测试通过！黑名单拦截机制工作正常')
        print('=' * 60)
    except AssertionError as e:
        print(f'\n❌ 测试失败: {e}')
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f'\n❌ 测试异常: {e}')
        import traceback
        traceback.print_exc()
