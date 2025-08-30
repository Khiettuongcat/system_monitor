# setup ubuntu or ubuntu server 
    
# install packet os
    sudo apt install dmidecode -y  
    sudo apt install ufw -y
# Down file sys_python
    cd sys_python
# Install packet sys.py
    pip3 install -r packet.txt
# run test file sys.py 
    python3 sys.py
# add auto run
    --get path folder sys.py
    sudo nano /etc/systemd/system/sys.service
    
    3 content nano

    [Unit]
    Description=Auto run sys.py at startup
    After=network.target
    
    [Service]
    ExecStart=/usr/bin/python3 /home/ubuntu/sys.py
    WorkingDirectory=/home/ubuntu
    Restart=always
    User=ubuntu
    
    [Install]
    WantedBy=multi-user.target
    
    sudo systemctl daemon-reload
    sudo systemctl enable sys.service
    sudo systemctl start sys.service
    
    5 check 
    systemctl status sys.service