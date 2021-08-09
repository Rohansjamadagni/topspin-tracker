import json
import eel
import os
import time
# load the config file
config = {}
with open("app_config.json", "r") as f:
	config = json.loads(f.read())

# Set web files folder
eel.init(config["web_folder"])

# Expose this function to Javascript
@eel.expose                         
def start_record(Generate_Coordinates):
    if(Generate_Coordinates):
        print("Generating Coords....")
        os.system('python3 Generate_Table_Coordinates.py')
    print("Starting to record...")
    os.system('ansible-playbook -i ../ansible/hosts.yml ../ansible/control.yml  &')
    # call control.yml
    return 

@eel.expose
def populate_tables():
    f = open("stroke_speed_result.json", "r")
    result = json.loads(f.read())
    f.close()
    eel.populate_tables_js(result)
    return

@eel.expose
def visualise():
    os.system('python3 visualization.py')


@eel.expose                         
def stop_recording():
    print("stop record and analyse")
    eel.publish_stage("Analysing Video...",0)
    os.system('ansible-playbook -i ../ansible/hosts.yml ../ansible/replay.yml')
    os.system('python3 pose_post_process.py')
    # os.system('python3 ball_speed_placement.py')
    eel.publish_stage("Video Successfully Analysed",100)
    eel.enable_button()
    return

# start the app
eel.start(config["index_page"], size=config["window_size"], mode=config["mode"])
