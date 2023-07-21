import sys
import random
import asyncio
import datetime
import time
from datetime import timedelta

import docker
import requests
from docker.types import ServiceMode
from prometheus_client import push_to_gateway, CollectorRegistry, Counter, Summary, Gauge

url = 'http://localhost:5001/{}'
registry = CollectorRegistry()
fail_response_count = Counter('fail_response_counter', 'count fail responses')
number_of_requests = Counter('number_of_requests', 'count number of requests')
online_user_count = Gauge('online_user_counter', 'count online users')
alive_worker_count = Gauge('alive_worker_counter', 'count alive workers')
success_response_count = Counter('success_response_counter', 'count success responses')
process_time_summary = Summary('process_time_summery', 'process time')
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
    else:
        node_workers = dict()
        for i in range(1, 200):
            node_workers[str(i)] = {
                service_worker_node_1: i,
                service_worker_node_2: 0
            }
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


def wait_for_running_server():
    require_services = {i: False for i in ["backend", "spark-worker", "spark-master", "prometheus"]}
    while True:
        print("check services are running?")
        all_running = True
        running_services = client.containers()
        for service_name in require_services:
            for service in running_services:
                for name in service.get("Names"):
                    if service_name in name:
                        if service.get("State") == "running":
                            require_services[service_name] = True

        for is_running in require_services.values():
            if not is_running:
                all_running = False

        if not all_running:
            time.sleep(20)
        else:
            time.sleep(20)
            break


async def main():
    loop = asyncio.get_event_loop()
    users_count = list(map(int, sys.argv[1].split(",")))
    workers_number = list(map(int, sys.argv[2].split(",")))
    data_files = sys.argv[3].split(",")
    user_duration = list(map(int, sys.argv[4].split(",")))
    servers_count = int(sys.argv[5])
    app_name = str(sys.argv[6]).replace(".py", "")
    think_times = list(map(int, sys.argv[7].split(",")))
    total_time = int(sys.argv[8])
    is_need_spark_session_stop = False
    is_need_sleep = False
    print("wait for running spark")
    wait_for_running_server()
    scale_workers(1, workers_number[0], servers_count)
    print("start workload")
    print("users_count", users_count)
    print("workers_number", workers_number)
    print("data_files", data_files)
    print("user_duration", user_duration)
    print("think_time", think_times)
    print("total_time", total_time)
    try:
        for index in range(len(users_count)):
            user_count = users_count[index]
            print(f'number of users: {user_count}')
            if index > 0 and workers_number[index - 1] != workers_number[index]:
                is_need_spark_session_stop = True
                is_need_sleep = True
                scale_workers(workers_number[index - 1], workers_number[index], servers_count)
                await asyncio.sleep(60)
            start_time = datetime.datetime.now()
            while datetime.datetime.now() - start_time < timedelta(seconds=user_duration[index]):
                print(datetime.datetime.now() - start_time)
                online_user_count.set(user_count)
                alive_worker_count.set(workers_number[index])
                request_list = list()
                before = time.time()
                for i in range(user_count):
                    request_list.append(
                        loop.run_in_executor(None, requests.get, url.format(app_name), {
                            'is_need_spark_session_stop': is_need_spark_session_stop,
                            'file_name': data_files[random.randint(0, len(data_files) - 1)]
                        })
                    )
                    is_need_spark_session_stop = False
                    number_of_requests.inc()
                    if is_need_sleep:
                        await asyncio.sleep(40)
                        is_need_sleep = False
                for i in range(len(request_list)):
                    response = await request_list[i]
                    await asyncio.sleep(think_times[index])
                    print(response.text)
                    if "Exception" not in response.text:
                        process_time_summary.observe(time.time() - before)
                        success_response_count.inc()
                    else:
                        fail_response_count.inc()
                push_metrics()
    except Exception as e:
        print(e)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
