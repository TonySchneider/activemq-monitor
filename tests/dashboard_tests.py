import requests
import time
import random

url = "http://localhost:8050/update_graph"

for _ in range(60):
    # Generate random numbers between 10 and 100 for each queue
    random_number_A = random.randint(10, 100)
    random_number_B = random.randint(10, 100)
    random_number_C = random.randint(10, 100)
    random_number_D = random.randint(10, 100)

    # Update the data
    data = {
        'queue_A': random_number_A,
        'queue_B': random_number_B,
        'queue_C': random_number_C,
        'queue_D': random_number_D
    }

    requests.get(url, params=data)
    time.sleep(1)  # Wait for one second
