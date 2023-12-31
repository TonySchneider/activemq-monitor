# ActiveMQ Monitor

**ActiveMQ Live Monitoring Dashboard**

This dashboard provides real-time monitoring capabilities for ActiveMQ brokers, filling a significant gap as ActiveMQ inherently lacks comprehensive real-time monitoring tools. At its core, our dashboard fetches and visualizes the delta in enqueue messages arriving at the queues, offering users and developers invaluable insights into message flow dynamics.

**Why Choose Our Dashboard?**

1. **AWS Integration**: While Amazon's Managed Message Broker service (Amazon MQ) does offer a monitoring solution through CloudWatch, our dashboard boasts a distinct advantage: reduced latency. By directly interfacing with the broker's admin XML URLs using straightforward HTTP requests, we provide near-instantaneous metric updates. This makes our dashboard more "live" compared to AWS CloudWatch.

2. **Ease of Use**: Designed with simplicity in mind, our tool facilitates smooth integration and deployment, regardless of whether you're a seasoned developer or just getting started with ActiveMQ.

3. **Cost-Effective**: Eliminate the need for third-party monitoring tools and enjoy a more immediate, direct view of your broker's performance without any added costs.

Equip yourself with a powerful real-time monitoring tool that offers both precision and immediacy. Dive in, and experience firsthand how our ActiveMQ Live Monitoring Dashboard can transform the way you monitor and manage your message queues.

![Functionality Demo](utils/example-graph.gif)

## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
3. [Docker Support](#docker-support)
4. [Testing](#testing)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/TonySchneider/activemq-monitor.git
cd activemq-monitor
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Setup environment variables:

```bash
export AMQ_HOSTS=broker1,broker2,broker3
export AMQ_USER=your_username
export AMQ_PASS=your_password
export AMQ_PORT=8162
```


2. launch the dashboard:

```bash
python dashboard_runner.py
```

Visit `http://localhost:8050` in your browser to view the dashboard.

## Docker Support

The `activemq_docker_example` directory provides Docker configuration for setting up a representative ActiveMQ environment. To use it:

1. Navigate to the `activemq_docker_example` directory:

```bash
cd activemq_docker_example
```

2. Build and start the Docker containers:

```bash
docker-compose up --build
```

## Testing

Run tests to verify dashboard functionality:

```bash
python tests/dashboard_tests.py
```

## Contributing

Feel free to raise issues or PRs if you think something could be better or if there's a bug in the code. Your contributions are always welcome!

## License

[MIT License](./LICENSE) (Include link to your LICENSE file if available)
