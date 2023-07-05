#!/usr/bin/env python3

from appium import webdriver
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime
import time
import concurrent.futures

# Initialize a Slack client
slack_client = WebClient(token='YOUR_SLACK_TOKEN')

# List of devices
devices = ['device1', 'device2', 'device3', 'device4', 'device5', 'device6', 'device7', 'device8', 'device9', 'device10']

def run_script(device):
    for i in range(3):
        try:
            # Connect to the device
            CAPABILITIES['deviceName'] = device
            APPIUM_DRIVER = webdriver.Remote('http://localhost:4723/wd/hub', CAPABILITIES)

            # Check if device is available
            if APPIUM_DRIVER.is_device_locked():
                raise Exception('Device is locked')

            # Run the script
            # Add your script here

            # If the script is successfully run, break the loop
            break
        except Exception as e:
            # If an error occurred, sleep for a while and then retry
            print(f'Attempt {i+1} failed for device {device}, retrying...')
            time.sleep(5)
    else:
        # If the script failed to run after 3 attempts, send a notification to Slack
        message = f'Script failed to run on device {device} after 3 attempts. Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        try:
            response = slack_client.chat_postMessage(channel='YOUR_SLACK_CHANNEL', text=message)
        except SlackApiError as e:
            print(f"Error sending message to Slack: {e.response['error']}")

# Run the script on all devices in parallel
with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(run_script, devices)
