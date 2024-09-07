# Weapon-system
### The weapon system is written with basic JS. the button functionality is to simulate an API call, and many more functionalities can be added.

## How to Run
> Access "docker" folder
> then build:
``` bash
sudo docker build -t weapon-system .
```
> Command to run the container:
``` bash
sudo docker run -p 5300:5300 --name weapon-system --network kr4k3n_net weapon-system
```
#### When you are running the container, make sure to access the url: http://localhost:5300 in browser, so that a js loop will start that will help in updating all the information.

![image](https://github.com/KR4K3N-CIP/Weapon-system/assets/18901770/93e0de56-0738-49c0-9edc-83e1b9e1335b)

_NOTE_ :if need to make any changes related to ip, port, url, etc.., access the config_standards.py in docker folder
