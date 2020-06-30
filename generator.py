# Script that takes in a command line argument N 
# and prints out the first N primes, and fibunacci numbers in parallel
# and posts the code and the output to a webhook
# For generating primes, I did not use a sieve method for two reasons
# 1: relying on a prime distribution function complicates 
# 2: using isPrime yields faster results initially, which might be more in line with goal of parallel execution
# I should also note that I had to look up muliprocessing details, specifically how to manage shared data

import os
from multiprocessing import Process, Manager, Value
from ctypes import c_char_p
import json
import requests
import math

# Prompts user for integer input
def prompt_user():
    msg = 'Please enter a number below:\n'
    while True:
        user_input = input(msg)
        if user_input.isdigit():
            return int(user_input)
        msg = 'Invalid! Please make sure to enter a valid number: \n'

# Generates the first n fibunacci numbers
# Iterative implementation O(N) time, O(1) space
def gen_fibs(n, output):
    (a, b, c) = (1, 1, 1)
    for i in range(1, n + 1):
        if i > 2:
            c = a + b
            a = b
            b = c
        line = 'FIB ' + str(i) + ': ' + str(c)
        print(line)
        output.value = output.value + line + '\n'

# Generates the first n prime numbers
# O(N*sqrt(N)) runtime, O(N) space
def gen_primes(n, output):
    (primes, i) = ([], 2)
    while len(primes) < n:
        if isPrime(primes, i):
            primes.append(i)
            line = 'PRIME ' + str(len(primes)) + ': ' + str(i)
            print(line)
            output.value = output.value + line + '\n'
        i += 1

# Checks if number in prime by determining divisibilty by primes less than its square root
# O(sqrt(N)) runtime, O(1) space
def isPrime(primes, i):
    bound = math.sqrt(i)
    for p in primes:
        if p > bound:
            break
        if i % p == 0:
            return False
    return True
    

# Posts code and output data (JSON) to webhook 
def submit(file_path, output_data):
    webhook_url = \
        'https://hooks.glip.com/webhook/38dbfcb8-57c2-49d6-a7c1-44ed88024ee0'
    data = {}
    with open(file_path, 'r') as f:
        data['code'] = f.read()
    data['output'] = output_data
    response = requests.post(webhook_url, data=json.dumps(data),
                             headers={'Content-Type': 'application/json'
                             })
    if response.status_code != 200:
        raise ValueError('Request returned an error %s, the response is:\n%s'
                          % (response.status_code, response.text))

if __name__ == '__main__':
    n = prompt_user()
    manager = Manager()
    output = manager.Value(c_char_p, '')
    file_path = './generator.py'
    p1 = Process(target=gen_primes, args=(n, output))
    p2 = Process(target=gen_fibs, args=(n, output))
    p1.start()
    p2.start()
    p1.join() 
    p2.join()
    # Once the two processes finish, we submit the output
    submit(file_path, output.value)
