#!/usr/bin/env python3

from appium import webdriver
from datetime import datetime
from os import getenv, path, makedirs
from time import sleep
import logging
import json
import requests
import concurrent.futures

# API Setup
API_KEY = getenv('HEADSPIN_SANDBOX')
API_URL = f'https://{API_KEY}@api-dev.headspin.io'
HEADER = {'Authorization': f'Bearer {API_KEY}'}

# List of devices
devices = [ {'UDID': 'R5CN20T5YYV', 'WD_ENDPOINT': f'https://dev-us-pao-1.headspin.io:7037/v0/{API_KEY}/wd/hub'},
            {'UDID': 'R58M33V7JGY', 'WD_ENDPOINT': f'https://dev-us-pao-1.headspin.io:7037/v0/{API_KEY}/wd/hub'},
            {'UDID': '9B061FFAZ00ENN', 'WD_ENDPOINT': f'https://dev-us-pao-5.headspin.io:7019/v0/{API_KEY}/wd/hub'}]


def log(device, message) -> None:
    # Get device id from device
    device_id = device['UDID']

    # Create a logger for the device
    logger = logging.getLogger(device_id)
    logger.setLevel(logging.INFO)

    # Create a file handler for the logger
    if not path.exists('device logs'):
        makedirs('device logs')
    file_handler = logging.FileHandler(f'device logs/{device_id}.log')

    # Create a formatter for the logger
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    # Log the message
    logger.info(message)

    # Remove the file handler from the logger to prevent duplicate logs
    logger.removeHandler(file_handler)


def unlock_device(device) -> str:
    '''
    make unlock device api call
    '''

    device_id = device['UDID']
    lock_device_url = f'{API_URL}/v0/devices/unlock'
    lock_device_data = json.dumps({"device_id": device_id})

    device_unlocked = False
    max_retries = 5
    retries = 0

    while not device_unlocked and retries < max_retries:
        try:
            r = requests.post(url=lock_device_url,
                                headers=HEADER, data=lock_device_data)
            reply = r.json()
            if reply["statuses"][0]["message"] == 'Device unlocked.':
                device_unlocked = True
            elif reply["statuses"][0]["message"] == 'Device is already unlocked.':
                if retries + 1 < max_retries:
                    raise Exception('Device is already unlocked.')
                else:
                    device_unlocked = True
        except Exception as e:
            log(device_id, f'Error releasing device: {e}')
            retries += 1
            sleep(5)  # Wait for 5 seconds before retrying


def run_script(device):
    while True:
        for i in range(3):
            try:
                # Connect to the device

                CAPABILITIES = {
                    "appium:udid": device['UDID'],
                    "appium:automationName": "uiautomator2",
                    "appium:platformName": "android",
                    "appium:appPackage": "com.android.settings",
                    "appium:appActivity": "com.android.settings.Settings",
                    "headspin:controlLock": True,
                    "headspin:resetUiAutomator2": True,
                    "appium:newCommandTimeout": 200
                }

                # Start driver
                try:
                    log(device, 'Appium Starting')
                    APPIUM_DRIVER = webdriver.Remote(device['WD_ENDPOINT'], CAPABILITIES)
                    log(device, 'Appium Started')
                except Exception as E:
                    # If an error occurred, raise a custom exception
                    log(device, f'Error: {E}')
                    raise AssertionError(
                        'Failed to start Appium driver') from E

                # Run the script
                log(device, 'Sleeping for 15')
                sleep(15)

                # If the script is successfully run, break the loop
                break
            except AssertionError as AE:
                log(device, f'Attempt {i+1} failed, force unlocking device and retrying...')
                unlock_device(device)
                continue

            except Exception as E:
                # If an error occurred, sleep for a while and then retry
                log(device, f'Attempt {i+1} failed, retrying...')
                sleep(5)

            finally:
                log(device, 'We now end the driver session')
                APPIUM_DRIVER.quit()
        else:
            # If the script failed to run after 3 attempts, print a message
            log(device, f'Script failed to run after 3 attempts. Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

        # Sleep for a while before running the script again
        sleep(5)
    
    log(device, 'YOU HAVE ENDED THE LOOP')


# Run the script on all devices in parallel
with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(run_script, devices)
