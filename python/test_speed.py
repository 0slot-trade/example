import requests
import time
import numpy as np

"""
### How to Choose a Node  ###
We provide nodes in three locations: Frankfurt, New York, and Amsterdam. It is recommended to select the node closest to your location.

### test script ###
This test script measures the maximum latency, minimum latency, average latency, and latency from the 10th to the 90th percentile during multiple access attempts. It helps you make an informed decision.  

Direct Installation:  
```
pip install requests numpy  
```

After successful installation, you can run the test:  
```
python test_speed.py  
```

It will output
```
Testing de_domain_url...
Successful requests: 1000/1000
Average time: 0.281030 seconds
Minimum time: 0.211010 seconds
Maximum time: 0.784061 seconds
10% percentile: 0.271020 seconds
20% percentile: 0.271345 seconds
30% percentile: 0.271595 seconds
40% percentile: 0.271856 seconds
50% percentile: 0.272114 seconds
60% percentile: 0.272448 seconds
70% percentile: 0.273095 seconds
80% percentile: 0.274257 seconds
90% percentile: 0.278987 seconds
Testing ny_domain_url...
Successful requests: 1000/1000
Average time: 0.289061 seconds
Minimum time: 0.253208 seconds
Maximum time: 1.742639 seconds
10% percentile: 0.254997 seconds
20% percentile: 0.258541 seconds
30% percentile: 0.265235 seconds
40% percentile: 0.272321 seconds
50% percentile: 0.278904 seconds
60% percentile: 0.287030 seconds
70% percentile: 0.294940 seconds
80% percentile: 0.302580 seconds
90% percentile: 0.307574 seconds
Testing ams_domain_url...
Successful requests: 1000/1000
Average time: 0.203582 seconds
Minimum time: 0.196838 seconds
Maximum time: 0.515168 seconds
10% percentile: 0.197338 seconds
20% percentile: 0.197577 seconds
30% percentile: 0.197782 seconds
40% percentile: 0.198032 seconds
50% percentile: 0.198368 seconds
60% percentile: 0.198760 seconds
70% percentile: 0.199504 seconds
80% percentile: 0.201145 seconds
90% percentile: 0.207533 seconds
```

Simply choose the node with the lowest latency as your sending node.If the latency exceeds 20ms, it is recommended to set up a machine near the node and test again.
"""

def test_url(url, num_requests):
    """
    Tests the performance of a URL by making multiple HTTP requests.
    
    Args:
        url (str): The URL to be tested
        num_requests (int): Number of requests to make
        
    Returns:
        tuple: (average_time, min_time, max_time, percentiles) if successful
               (None, None, None, None) if no successful requests
    """
    # Create a session object for connection pooling
    session = requests.Session()
    
    # Initialize performance metrics
    total_time = 0
    successful_requests = 0
    min_time = float('inf')  # Initialize with infinity
    max_time = 0 
    times = []  # List to store all response times
    
    # Make multiple requests to test performance
    for _ in range(num_requests):
        try:
            # Record start time before making request
            start_time = time.time()
            
            # Make GET request to the URL
            response = session.get(url)
            
            # Record end time after receiving response
            end_time = time.time()
            
            # Calculate elapsed time for this request
            elapsed_time = end_time - start_time
            
            # Update metrics
            total_time += elapsed_time
            successful_requests += 1
            times.append(elapsed_time)

            # Update min and max times
            if elapsed_time < min_time:
                min_time = elapsed_time
            if elapsed_time > max_time:
                max_time = elapsed_time
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

    # Calculate and display statistics if we had successful requests
    if successful_requests > 0:
        # Calculate average response time
        avg_time = total_time / successful_requests
        
        # Print basic statistics
        print(f"Successful requests: {successful_requests}/{num_requests}")
        print(f"Average time: {avg_time:.6f} seconds")
        print(f"Minimum time: {min_time:.6f} seconds")
        print(f"Maximum time: {max_time:.6f} seconds")

        # Calculate various percentiles (10% to 90%)
        percentiles = np.percentile(times, [10, 20, 30, 40, 50, 60, 70, 80, 90])
        
        # Print percentile information
        for i, percentile in enumerate(percentiles):
            print(f"{10 * (i + 1)}% percentile: {percentile:.6f} seconds")

        return avg_time, min_time, max_time, percentiles
    else:
        print("No successful requests.")
        return None, None, None, None

# Number of requests to be made for testing
num_requests = 1000

de_domain_url = "http://de1.0slot.trade/?api-key=xxx"
ny_domain_url = "http://ny1.0slot.trade/?api-key=xxx"
ams_domain_url = "http://ams1.0slot.trade/?api-key=xxx"

print("Testing de_domain_speed...")
test_url(de_domain_url, num_requests)

print("Testing ny_domain_speed...")
test_url(ny_domain_url, num_requests)

print("Testing ams_domain_speed...")
test_url(ams_domain_url, num_requests)