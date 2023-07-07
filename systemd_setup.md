Python script as a service in Ubuntu 18.04 using systemd, which is the init system used in Ubuntu to bootstrap the user space and manage all processes subsequently.

1. First, you need to make sure your Python script is executable. You can do this by adding a shebang line at the top of your script:

```python
#!/usr/bin/env python3

# rest of your script
```

2. Then, you need to make the script file executable by running the following command in the terminal:

```bash
chmod +x /path/to/your/script.py
```

3. Now, you can create a systemd service file for your script. Create a new file in `/etc/systemd/system/`, for example `/etc/systemd/system/myappium.service`, with the following content:

```ini
[Unit]
Description=My Appium Script
After=network.target

[Service]
ExecStart=/path/to/your/script.py
Restart=always
User=yourusername
Group=yourgroup
Environment=PATH=/usr/bin:/usr/local/bin
Environment=PYTHONPATH=/path/to/your/python/environment
WorkingDirectory=/path/to/your/working/directory

[Install]
WantedBy=multi-user.target
```

Replace `/path/to/your/script.py` with the actual path to your Python script, `yourusername` and `yourgroup` with your actual username and group, `/path/to/your/python/environment` with the path to your Python environment if you're using one, and `/path/to/your/working/directory` with the path to the directory where your script is located.

4. After creating the service file, you can start your service by running:

```bash
sudo systemctl start myappium
```

5. If you want your service to start automatically at boot, you can enable it by running:

```bash
sudo systemctl enable myappium
```

6. You can check the status of your service by running:

```bash
sudo systemctl status myappium
```

Please note that you need to have root privileges to create and manage systemd services. Also, this method only works on systems that use systemd, which includes most modern Linux distributions. If you're using a different system, the method for running your script as a service may be different.

