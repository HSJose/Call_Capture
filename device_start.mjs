import { remote } from 'webdriverio';
import fetch from 'node-fetch';
import fs from 'fs';
import { promisify } from 'util';
import { join } from 'path';
import pLimit from 'p-limit';

const sleep = promisify(setTimeout);

const API_KEY = process.env['HEADSPIN_SANDBOX'];
const API_URL = `https://${API_KEY}@api-dev.headspin.io`;
const HEADER = { 'Authorization': `Bearer ${API_KEY}` };

const devices = [
    { 'UDID': 'R5CN20T5YYV', 'WD_ENDPOINT': `https://dev-us-pao-1.headspin.io:7037/v0/${API_KEY}/wd/hub` },
    { 'UDID': 'R58M33V7JGY', 'WD_ENDPOINT': `https://dev-us-pao-1.headspin.io:7037/v0/${API_KEY}/wd/hub` },
    { 'UDID': '9B061FFAZ00ENN', 'WD_ENDPOINT': `https://dev-us-pao-5.headspin.io:7019/v0/${API_KEY}/wd/hub` }
];

const log = (device, message) => {
    const deviceId = device['UDID'];
    if (!fs.existsSync('device logs')) {
        fs.mkdirSync('device logs');
    }
    const logPath = join('device logs', `${deviceId}.log`);
    fs.appendFileSync(logPath, `${new Date().toISOString()} : ${message}\n`);
};

const unlockDevice = async (device) => {
    const deviceId = device['UDID'];
    const lockDeviceUrl = `${API_URL}/v0/devices/unlock`;
    const lockDeviceData = JSON.stringify({ "device_id": deviceId });

    let deviceUnlocked = false;
    let maxRetries = 5;
    let retries = 0;

    while (!deviceUnlocked && retries < maxRetries) {
        try {
            const res = await fetch(lockDeviceUrl, { method: 'POST', headers: HEADER, body: lockDeviceData });
            const reply = await res.json();
            if (reply["statuses"][0]["message"] === 'Device unlocked.') {
                deviceUnlocked = true;
            } else if (reply["statuses"][0]["message"] === 'Device is already unlocked.') {
                if (retries + 1 < maxRetries) {
                    throw new Error('Device is already unlocked.');
                } else {
                    deviceUnlocked = true;
                }
            }
        } catch (e) {
            log(device, `Error releasing device: ${e}`);
            retries++;
            await sleep(5000);
        }
    }
};

const runScript = async (device) => {
    while (true) {
        for (let i = 0; i < 3; i++) {
            let client;
            try {
                const capabilities = {
                    "udid": device['UDID'],
                    "automationName": "uiautomator2",
                    "platformName": "android",
                    "appPackage": "com.android.settings",
                    "appActivity": "com.android.settings.Settings",
                    "headspin:controlLock": true,
                    "headspin:resetUiAutomator2": true,
                    "newCommandTimeout": 200
                };

                log(device, 'Appium Starting');
                client = await remote({
                    logLevel: 'silent',
                    path: device['WD_ENDPOINT'],
                    capabilities
                });
                log(device, 'Appium Started');

                log(device, 'Sleeping for 15');
                await sleep(15000);
                break;
            } catch (E) {
                log(device, `Attempt ${i+1} failed, force unlocking device and retrying...`);
                await unlockDevice(device);
            } finally {
                log(device, 'We now end the driver session');
                if (client) {
                    await client.deleteSession();
                }
            }
        }
        log(device, `Script failed to run after 3 attempts. Timestamp: ${new Date().toISOString()}`);
        await sleep(5000);
    }
};

const concurrency = 3; 
const limit = pLimit(concurrency);
const tasks = devices.map(device => limit(() => runScript(device)));

Promise.all(tasks).then(() => console.log('All scripts have been started.'));
