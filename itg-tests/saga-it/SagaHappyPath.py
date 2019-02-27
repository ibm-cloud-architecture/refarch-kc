# load the order request from json
import json
f = open('../data/FreshProductOrder.json','r')
order = json.load(f)
print(order)

import requests

response = requests.get('https://httpbin.org/ip')

print('Your IP is {0}'.format(response.json()['origin']))

# call create order service
res = requests.post("http://ordercmd:9080/orders",json=order)
print(res)

# listen to orders topic, verify orderCreated event was published

# listen to orders topic to verify voyage allocated to order

# listen to orders topic to verify container was allocated to order

# listen to orders topic to verify ship planned to move container 