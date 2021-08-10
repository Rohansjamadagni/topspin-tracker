# Topspin Trackers

The repository for The OpenCV AI Competition 2021 Phase II

Link to the [demo](https://youtu.be/1SICV66rsxU)

### Region
Central Asia + Southern Asia (Bangalore, India)

### Team Members
- [Kaustubh Kulkarni](https://github.com/KulkarniKaustubh)
- [Rohan Jamadagni](https://github.com/Rohansjamadagni)
- [Jeffrey Paul](https://github.com/jeffreypaul15)
- [Sucheth Shenoy](https://github.com/sucheth17)

---

## System Setup

3 OAK-Ds are required for the setup.

First,

```sh
git clone https://github.com/Rohansjamadagni/topspin-tracker.git
cd topspin-tracker
```

### OAK-D 1 and OAK-D 2

These OAK-Ds must be mounted on the net clamps in such a way that the cameras face the player being analysed.

On the systems interfacing with the OAK-Ds, run
```sh
pip install -r pose_estimation/requirements.txt
```

Connect 2 vibration sensors to one of the systems and place the sensors under the table, one on each side.

### OAK-D 3

This OAK-D must be placed at an elevated umpire's view.

On the system interfacing with this OAK-D, run
```sh
pip install -r ball_detection/requirements.txt
```

### Server

On the server, run
```sh
sudo apt install ansible
pip install -r server/requirements.txt
```

## Run System

To run the application, first the 3 systems should be connected to the same network.

Open the `hosts.yml` file in the `ansible` folder. The IP addresses for the 3 systems must be entered here. Make sure that the IP address of the system entered for `pose_estimator_1` also has the vibration sensors connected to it.

Next, the `ips.json` file must be updated with the host machine's , i.e. the server's IP address in the `broker_ip` field.

Once this is done, run
```sh
ansible-playbook -i ansible/hosts.yml ansible/init.yml
python3 server/subscriber.py
```

This will initialise all systems with the required code and folder structure.

You're all done! The following command will start the graphical application to record and analyse your sessions.

```sh
python3 server/app.py
```
