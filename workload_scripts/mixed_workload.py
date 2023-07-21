import json
import sys
import asyncio
import datetime
import time
from datetime import timedelta
from typing import List

import docker
import requests
from docker.types import ServiceMode
from prometheus_client import push_to_gateway, CollectorRegistry, Counter, Summary, Gauge

url = 'http://localhost:5001/{}'
registry = CollectorRegistry()
fail_response_count = Counter('fail_response_counter', 'count fail responses', ['method', 'file'])
success_response_count = Counter('success_response_counter', 'count success responses', ['method', 'file'])
number_of_requests = Counter('number_of_requests', 'count number of requests', ['method', 'file'])
online_user_count = Gauge('online_user_counter', 'count online users')
alive_worker_count = Gauge('alive_worker_counter', 'count alive workers')
process_time_summary = Summary('process_time_summery', 'process time', ['method', 'file'])
registry.register(fail_response_count)
registry.register(number_of_requests)
registry.register(online_user_count)
registry.register(alive_worker_count)
registry.register(success_response_count)
registry.register(process_time_summary)


def push_metrics():
    global registry
    push_to_gateway('http://localhost:9091', job="spark", registry=registry)


client = docker.APIClient()
service_worker_node_1 = 'test_masterspark-worker'
service_worker_node_2 = 'test_spark-worker'


def make_node_workers(servers_count: int) -> dict:
    if servers_count == 2:
        node_workers = dict()
        node_1 = 1
        node_2 = 0
        for i in range(1, 400):
            node_workers[str(i)] = {
                service_worker_node_1: node_1,
                service_worker_node_2: node_2
            }
            if i % 2 == 0:
                node_1 += 1
            else:
                node_2 += 1
        # node_workers = {
        #     "1": {
        #         service_worker_node_1: 1,
        #         service_worker_node_2: 0
        #     },
        #     "2": {
        #         service_worker_node_1: 1,
        #         service_worker_node_2: 1
        #     },
        #     "3": {
        #         service_worker_node_1: 2,
        #         service_worker_node_2: 1
        #     },
        #     "4": {
        #         service_worker_node_1: 2,
        #         service_worker_node_2: 2
        #     }
        # }
    else:
        node_workers = dict()
        for i in range(1, 200):
            node_workers[str(i)] = {
                service_worker_node_1: i,
                service_worker_node_2: 0
            }
        # node_workers = {
        #     "1": {
        #         service_worker_node_1: 1,
        #         service_worker_node_2: 0
        #     },
        #     "2": {
        #         service_worker_node_1: 2,
        #         service_worker_node_2: 0
        #     },
        #     "3": {
        #         service_worker_node_1: 3,
        #         service_worker_node_2: 0
        #     },
        #     "4": {
        #         service_worker_node_1: 4,
        #         service_worker_node_2: 0
        #     }
        # }
    return node_workers


def scale_workers(prev_worker_counts: int, worker_counts: int, servers_count: int):
    node_workers = make_node_workers(servers_count)
    for node, node_worker_counts in node_workers.get(str(worker_counts)).items():
        prev_node_worker_counts = node_workers.get(str(prev_worker_counts)).get(node)
        if prev_node_worker_counts != node_worker_counts:
            print(f'scale service {node} from {prev_node_worker_counts} to {node_worker_counts} replicas starting')
            inspect = client.inspect_service(node)
            svc_version = inspect['Version']['Index']
            svc_id = inspect['ID']
            update_config = docker.types.UpdateConfig(delay=0, parallelism=0, failure_action='rollback',
                                                      order='start-first')
            client.update_service(
                svc_id, svc_version, name=node,
                mode=ServiceMode('replicated', replicas=node_worker_counts),
                fetch_current_spec=True, update_config=update_config
            )
            print(f'scale service {node} from {prev_node_worker_counts}  to {node_worker_counts} replicas done')


def divide_data_files(percentages: list, count: int):
    t = {}
    start = 0
    last_j = 0
    for i, j in enumerate(percentages):
        for k in range(start, int(count * (j + last_j) / 100)):
            t[k] = i
        start = int(count * (j + last_j) / 100)
        last_j += j
    return t


async def get_request(loop, method, is_need_spark_session_stop, data_file_name):
    print(f"request to {method} sent")
    before = time.time()
    number_of_requests.labels(method=method, file=data_file_name).inc()
    executor = loop.run_in_executor(None, requests.get, url.format(method),
                                    {'is_need_spark_session_stop': is_need_spark_session_stop,
                                     'file_name': data_file_name})

    response = await executor
    print("response of ", method, "received: ", response.text)
    if "Exception" not in response.text:
        process_time_summary.labels(method=method, file=data_file_name).observe(time.time() - before)
        success_response_count.labels(method=method, file=data_file_name).inc()
    else:
        fail_response_count.labels(method=method, file=data_file_name).inc()


async def main():
    loop = asyncio.get_event_loop()
    config = sys.argv[1]
    print(config)
    config = json.loads(config)
    is_need_spark_session_stop = False
    is_need_sleep = False
    print("wait for running spark")
    time.sleep(60)
    print("start workload")
    servers_count = int(config["server_config"]["server_counts"])
    spark_worker_counts = int(config["server_config"]["spark_worker_counts"])
    scale_workers(1, spark_worker_counts, servers_count)
    time.sleep(30)
    time_in_second = int(config["workload_config"]["time_in_second"])
    user_count = int(config["workload_config"]["users_count"])
    apps: List[dict] = config["workload_config"]["apps"]
    try:
        print(f'number of users: {user_count}')
        start_time = datetime.datetime.now()
        while datetime.datetime.now() - start_time < timedelta(seconds=time_in_second):
            print(datetime.datetime.now() - start_time)
            online_user_count.set(user_count)
            alive_worker_count.set(spark_worker_counts)
            request_list = list()
            for app in apps:
                users_app = int(int(app["user_percentage"]) * user_count / 100)
                tmp_files = divide_data_files(app["data_file_percentage"], users_app)
                for i in range(users_app):
                    method = str(app["app_name"]).replace(".py", "")
                    request_list.append(
                        get_request(loop, method, is_need_spark_session_stop, app["data_files"][tmp_files[i]])
                    )
                    is_need_spark_session_stop = False
                    if is_need_sleep:
                        await asyncio.sleep(40)
                        is_need_sleep = False
            await asyncio.gather(*request_list)
            push_metrics()
    except Exception as e:
        print(e)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
