# ActiveMQ Monitor

Monitor your ActiveMQ brokers by fetching real-time metrics and visualizing them in a comprehensive dashboard.

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
