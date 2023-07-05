#!/usr/bin/env python3

from appium import webdriver
from datetime import datetime
from os import getenv
from time import sleep
import json
import requests
import concurrent.futures

# API Setup
API_KEY = getenv('HEADSPIN_SANDBOX')
API_URL = f'https://{API_KEY}@api-dev.headspin.io'
HEADER = {'Authorization': f'Bearer {API_KEY}'}

# List of devices
devices = ['R5CN20T5YYV', 'R58M33V7JGY', '9B061FFAZ00ENN']


def log(device_id, message) -> None:
    if device_id:
        print(f'{datetime.now()} {device_id}: {message}')
    else:
        print(f'{datetime.now()} : {message}')


def unlock_device(device_id) -> str:
        '''
        make unlock device api call
        '''
        lock_device_url = f'{API_URL}/v0/devices/unlock'
        lock_device_data = json.dumps({"device_id": device_id})

        device_unlocked = False
        max_retries = 5
        retries = 0

        while not device_unlocked and retries < max_retries:
            try:
                r = requests.post(url=lock_device_url, headers=HEADER, data=lock_device_data)
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

                WD_ENDPOINT = f'https://appium-dev.headspin.io:443/v0/{API_KEY}/wd/hub'

                CAPABILITIES = {
                  "appium:udid": device,
                  "appium:automationName": "uiautomator2",
                  "appium:platformName": "android",
                  "appPackage": "com.android.settings",
                  "appActivity": "com.android.settings.Settings",
                  "headspin:controlLock": True,
                  "headspin:resetUiAutomator2": True,
                  "appium:newCommandTimeout": 200
                }
                
                # Start driver
                try:
                  log(device, 'Appium Starting')
                  APPIUM_DRIVER = webdriver.Remote(WD_ENDPOINT, CAPABILITIES)
                  log(device, 'Appium Started')
                except Exception as E:
                  # If an error occurred, raise a custom exception
                  print(f'Error: {E}')
                  raise AssertionError('Failed to start Appium driver') from E

                # Run the script
                log(device, 'Sleeping for 15')
                sleep(15)
                
                # If the script is successfully run, break the loop
                break
            except AssertionError as AE:
                print(f'Attempt {i+1} failed for device {device}, force unlocking device and retrying...')
                unlock_device(device)
                continue
            
            except Exception as E:
                # If an error occurred, sleep for a while and then retry
                print(f'Attempt {i+1} failed for device {device}, retrying...')
                sleep(5)

            finally:
                log(device, 'We now end the driver session')
                APPIUM_DRIVER.quit()
        else:
            # If the script failed to run after 3 attempts, print a message
            print(f'Script failed to run on device {device} after 3 attempts. Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

        # Sleep for a while before running the script again
        sleep(5)

# Run the script on all devices in parallel
with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(run_script, devices)
