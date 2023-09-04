import os
import sys
import time
import dash
import logging
import requests
import xmltodict
from typing import Union
from dash import dcc, html
from collections import deque
from dotenv import load_dotenv
import plotly.graph_objs as go
from flask import Flask, request
from threading import Lock, Thread
from datetime import datetime, timedelta
from dash.dependencies import Input, Output
from concurrent.futures import ThreadPoolExecutor

from helpers.various_helpers import convert_comma_separated_str_to_list

# SETUP FOR METRICS FETCHER
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-3s | %(message)s', stream=sys.stdout)

try:
    AMQ_HOSTS = os.environ.get("AMQ_HOSTS")
    AMQ_USER = os.environ.get("AMQ_USER")
    AMQ_PASS = os.environ.get("AMQ_PASS")
    AMQ_PORT = os.environ.get("AMQ_PORT") or 8162
    assert all(key is not None for key in [AMQ_HOSTS, AMQ_USER, AMQ_PASS, AMQ_PORT])

    AMQ_HOSTS = convert_comma_separated_str_to_list(AMQ_HOSTS)
except AssertionError:
    logging.error("Didn't get the mandatory env vars.")

total_queues_metrics = {}
prev_enqueued_metrics = {}


def _extract_queues_details(queue_object: dict) -> dict:
    return {metric.strip('@'): int(value) for metric, value in queue_object['stats'].items()}


def get_broker_metrics_by_queue(queue_name: str, broker_host: str) -> dict:
    queue_metrics = None
    headers = {'Accept': 'application/json'}

    # Use the broker_host in the URL
    res = requests.get(f"https://{broker_host}:{AMQ_PORT}/admin/xml/queues.jsp", auth=(AMQ_USER, AMQ_PASS),
                       headers=headers)
    broker_details = xmltodict.parse(res.content)
    queues_object: Union[list, dict] = broker_details["queues"]["queue"]
    if isinstance(queues_object, list):
        queues_by_name = list(filter(lambda x: x['@name'] == queue_name, queues_object))
        if queues_by_name:
            queue_metrics = _extract_queues_details(queues_by_name[0])
    elif isinstance(queues_object, dict):
        queue_metrics = _extract_queues_details(queues_object) if queues_object['@name'] == queue_name else None

    return queue_metrics


def update_queues_metrics(queue_name: str, broker_host: str, shared_metrics_calculation: dict, thread_lock: Lock):
    # We'll pass the broker_host to get metrics specific to a broker
    broker_metrics = get_broker_metrics_by_queue(queue_name=queue_name, broker_host=broker_host)

    if broker_metrics and 'enqueueCount' in broker_metrics:
        enqueue_delta = broker_metrics['enqueueCount'] - prev_enqueued_metrics.get(queue_name, 0)
        prev_enqueued_metrics[queue_name] = broker_metrics['enqueueCount']
        with thread_lock:
            # accumulate the delta across brokers
            shared_metrics_calculation[queue_name] = shared_metrics_calculation.get(queue_name, 0) + enqueue_delta


def metric_updater():
    global total_queues_metrics
    thread_lock = Lock()

    while True:
        shared_metrics_calculation = {}
        logging.debug("Updating metrics...")

        # get queues details
        queues = [f"QUEUE/{Q}" for Q in ['A', 'B', 'C', 'D']]

        # separate the hosts
        broker_hosts = AMQ_HOSTS.split(',')

        workers = []
        with ThreadPoolExecutor(max_workers=len(queues) * len(broker_hosts)) as executor:
            for queue in queues:
                for broker_host in broker_hosts:
                    workers.append(executor.submit(update_queues_metrics, queue, broker_host, shared_metrics_calculation, thread_lock))

        # wait until all threads were finished at this iteration
        for worker in workers:
            worker.result()

        total_queues_metrics = shared_metrics_calculation
        logging.info(f"Metrics were updated.")


def metric_analyser():
    while True:
        if total_queues_metrics:
            # update the dashboard
            params = {
                'queue_A': total_queues_metrics.get('QUEUE/A', 0),
                'queue_B': total_queues_metrics.get('QUEUE/B', 0),
                'queue_C': total_queues_metrics.get('QUEUE/C', 0),
                'queue_D': total_queues_metrics.get('QUEUE/D', 0)
            }
            requests.get("http://localhost:8050/update_graph", params=params)

            logging.info(f"Delta metrics at this moment: '{total_queues_metrics}'.")
        time.sleep(1)


# Deque objects for each queue
X = deque(maxlen=60)
Y1 = deque(maxlen=60)
Y2 = deque(maxlen=60)
Y3 = deque(maxlen=60)
Y4 = deque(maxlen=60)

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.config.suppress_callback_exceptions = True
queue_names = ['A', 'B', 'C', 'D']

app.layout = html.Div(
    [
        html.Div(
            id='live-clock',
            style={'fontSize': '16px', 'textAlign': 'left', 'padding': '10px'}
        ),
        html.Div(
            "Monitoring Dashboard",
            style={'textAlign': 'center', 'fontSize': '40px', 'color': 'black', 'font-weight': 'bold', 'padding': '10px'}
        ),
        # Row 1
        html.Div([
            dcc.Graph(id='live-graph-1', animate=True, style={'width': '50%', 'display': 'inline-block'}),
            dcc.Graph(id='live-graph-2', animate=True, style={'width': '50%', 'display': 'inline-block'})
        ]),

        # Row 2
        html.Div([
            dcc.Graph(id='live-graph-3', animate=True, style={'width': '50%', 'display': 'inline-block'}),
            dcc.Graph(id='live-graph-4', animate=True, style={'width': '50%', 'display': 'inline-block'})
        ]),

        dcc.Interval(
            id='graph-update',
            interval=1000,
            n_intervals=0
        ),

    ]
)


@app.callback(
    Output('live-clock', 'children'),
    [Input('clock-update', 'n_intervals')]
)
def update_clock(n):
    return str(datetime.now().replace(microsecond=0))


@app.callback(
    [Output('live-graph-1', 'figure'),
     Output('live-graph-2', 'figure'),
     Output('live-graph-3', 'figure'),
     Output('live-graph-4', 'figure')],
    [Input('graph-update', 'n_intervals')]
)
def update_graphs(n):
    def generate_layout(queue_name):
        return {
            'layout': go.Layout(
                title=f'Message Per Second - Queue {queue_name}',
                xaxis=dict(
                    title='Time',
                    type='date',
                    range=[(max(X) - timedelta(seconds=60)).isoformat(), max(X).isoformat()] if X else None
                ),
                yaxis=dict(title='Enqueue Messages'),
                height=300,
                autosize=True
            )
        }

    data1 = [go.Scatter(x=list(X), y=list(Y1), name='Queue A', mode='lines+markers')] if X and Y1 else []
    data2 = [go.Scatter(x=list(X), y=list(Y2), name='Queue B', mode='lines+markers')] if X and Y2 else []
    data3 = [go.Scatter(x=list(X), y=list(Y3), name='Queue C', mode='lines+markers')] if X and Y3 else []
    data4 = [go.Scatter(x=list(X), y=list(Y4), name='Queue D', mode='lines+markers')] if X and Y4 else []

    return {'data': data1, **generate_layout(queue_names[0])}, {'data': data2, **generate_layout(queue_names[1])}, {'data': data3, **generate_layout(queue_names[2])}, {'data': data4, **generate_layout(queue_names[3])}


@server.route('/update_graph', methods=['GET'])
def update_data():
    global X, Y1, Y2, Y3, Y4

    queue_A = request.args.get('queue_A')
    queue_B = request.args.get('queue_B')
    queue_C = request.args.get('queue_C')
    queue_D = request.args.get('queue_D')

    dt = datetime.now().replace(microsecond=0)
    X.append(dt)

    if queue_A is not None:
        Y1.append(float(queue_A))
    if queue_B is not None:
        Y2.append(float(queue_B))
    if queue_C is not None:
        Y3.append(float(queue_C))
    if queue_D is not None:
        Y4.append(float(queue_D))

    return "OK", 200


if __name__ == '__main__':
    Thread(target=metric_analyser).start()
    app.run_server(host='0.0.0.0', debug=True)
