## System Setup

1. Create a Systemd Timer and Service File. 

        sudo nano /etc/systemd/system/my_script.timer 

        sudo nano /etc/systemd/system/my_script.service 

    <!-- 3. Sample content to timer file.  -->
 

2. Reload systemd and enable the service: 

        sudo systemctl daemon-reload 

        sudo systemctl enable my_script.service 

        sudo systemctl enable my_script.timer 

 

3. Start the service: 

        sudo systemctl start my_script.service 

        sudo systemctl start my_script.timer 

4. Check the status: 

        sudo systemctl status my_script.timer 

        sudo systemctl status  my_script.service 

5. Stop the service

        sudo systemctl stop my_script.timer 

        sudo systemctl stop  my_script.service 