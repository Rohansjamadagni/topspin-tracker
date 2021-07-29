import subprocess
import os

def ansible_destroy():
    os.system('ansible-playbook -i ../ansible/hosts ../ansible/packed.yml')

def ansible_ping(device):
    command = 'ansible all -m ping -v'
    p = subprocess.check_output(command.split(' '))

def start_record():
    os.system('ansible-playbook -i ../ansible/hosts ../ansible/control.yml  &')

def start_replay():
    os.system('ansible-playbook -i ../ansible/hosts ../ansible/replay.yml  &')

def take_picture():
    os.system('ansible-playbook -i ../ansible/hosts.yml ../ansible/picture.yml')

