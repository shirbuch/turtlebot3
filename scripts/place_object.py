#!/usr/bin/env python

from __future__ import print_function
import subprocess
import rospy
from pick_balls_turtlebot3.srv import PlaceObject,PlaceObjectResponse
from geometry_msgs.msg import Pose
from gazebo_msgs.srv import SpawnModel, DeleteModel, DeleteModelRequest
from gazebo_msgs.msg import ModelStates, ModelState
from tf.transformations import quaternion_from_euler, euler_from_quaternion

# todo make it work on installed env, fix duplicate from pick_object and control
GAZEBO_PATH = subprocess.getoutput("rospack find turtlebot3_gazebo")

# todo fix duplicate from control and pick_object
def spawn_model(name, file_location=GAZEBO_PATH+'/models/objects/red_ball.sdf', spawn_location=[0.0,0.0,1.0]):
    #rospy.init_node('spawn_model', log_level=rospy.INFO)
    pose = Pose()
    pose.position.x = spawn_location[0]
    pose.position.y = spawn_location[1]
    pose.position.z = spawn_location[2]
    spawn_model_client = rospy.ServiceProxy('/gazebo/spawn_sdf_model', SpawnModel)
    spawn_model_client(model_name=name,
                       model_xml=open(file_location, 'r').read(),
                       robot_namespace='/stuff', initial_pose=pose, reference_frame='world')

# todo fix duplicate from control and pick_object
def delete_model(name):
    # delete model
    srv = rospy.ServiceProxy('/gazebo/delete_model', DeleteModel)
    req = DeleteModelRequest()
    req.model_name = name
    resp = srv(req)

# todo fix duplicate from sense_pose and pick_object or use sense_pose service
def gps_location():
    # request a GPS like pose information from the Gazebo server
    rospy.loginfo("Requesting Global Robot Pose from Gazebo")
    model_state = rospy.wait_for_message("gazebo/model_states", ModelStates)
    me_pose = Pose()
    me_pose = model_state.pose[2]
    me_pose_angles = euler_from_quaternion([me_pose.orientation.x, me_pose.orientation.y, me_pose.orientation.z, me_pose.orientation.w])
    print('My pose is (x,y,theta): ')
    print(me_pose.position.x, me_pose.position.y, me_pose_angles[2])
    return me_pose.position.x, me_pose.position.y, me_pose_angles[2]

# Service logic
def place_object(object):
    print(f"place_object: {object.name}")
    # todo check if in knapsack
    delete_model(object.name)
    me_pose = gps_location()
    spawn_model(name=object.name, spawn_location=[me_pose[0]+0.15, me_pose[1]+0.15, 1.0])

def handle_place_object(req):
    try:
        place_object(req.object)
        return PlaceObjectResponse()
    except rospy.ROSInterruptException as e:
        print(f"Error: {e}")

def place_object_server():
    rospy.init_node('place_object_server')
    s = rospy.Service('place_object', PlaceObject, handle_place_object)
    print("Ready to place object.")
    rospy.spin()

if __name__ == "__main__":
    place_object_server()