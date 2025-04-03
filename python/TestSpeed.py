import requests
import time
import numpy as np

# The domain URL to be tested with API key placeholder
domain_url = "http://de1.0slot.trade/?api-key=xxx"

# Number of requests to be made for testing
num_requests = 1000

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

# Execute the test for the domain URL
print("Testing domain URL...")
domain_avg_time, domain_min_time, domain_max_time, domain_percentiles = test_url(domain_url, num_requests)
