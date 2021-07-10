import subprocess
import os

def ansible_destroy():
    os.system('ansible-playbook -i ../ansible/hosts ../ansible/packed.yml')

def ansible():
    os.system('ansible-playbook -i ../ansible/hosts ../ansible/control.yml --tags "mqtt_connect" &')

def ansible_ping(device):
    command = 'ansible all -m ping -v'
    p = subprocess.check_output(command.split(' '))

def start_record():
    os.system('ansible-playbook -i ../ansible/hosts ../ansible/control.yml --tags "start_record" &')

def start_replay():
    os.system('ansible-playbook -i ../ansible/hosts ../ansible/control.yml --tags "start_replay" &')
