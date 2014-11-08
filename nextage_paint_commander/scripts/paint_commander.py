#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Koji Terada
# @file paint_commander.py                                                          

import moveit_commander
import rospy
import geometry_msgs.msg
import copy

# 軌道をスケーリングするパラメータ[m]
TRAJECTORY_SCALE = 0.1

# hand持ち上げ高さ[m]
LIFT_HEIGHT = 0.02

from find_contours.srv import FindContours

def main():
    rospy.init_node("paint_commander")

    robot = moveit_commander.RobotCommander()
    
    print robot.get_group_names()

    print robot.get_current_state()

    rarm = moveit_commander.MoveGroupCommander("right_arm")
    larm = moveit_commander.MoveGroupCommander("left_arm")

    larm_init_pose = larm.get_current_pose().pose

    # 軌道を取込
    find_cont = rospy.ServiceProxy('find_contours/find_contours', FindContours)
    trajectories = find_cont().contours
    
    print "Find %d trajectories."%len(trajectories)
    
    waypoints = []

    # 最初に少しだけ持ち上げる
    waypoints.append(larm_init_pose)
    init_lift = copy.deepcopy(larm_init_pose)
    init_lift.position.z += LIFT_HEIGHT
    
    larm.set_pose_target(init_lift)
    larm.go()
    #waypoints.append(copy.deepcopy(init_lift))

    # (plan, fraction) = larm.compute_cartesian_path(waypoints, 0.01, 0.0)
    # rospy.sleep(plan.joint_trajectory.points[-1].time_from_start)
    rospy.sleep(2)
    
    print "=" * 10, " lift hand."
    # larm.execute(plan)
    # rospy.sleep(5)
    
    for trajectory in trajectories:
        waypoints = []

        trajectory_init = copy.deepcopy(init_lift)
        trajectory_init.position.x = trajectory_init.position.x + TRAJECTORY_SCALE * trajectory.points[0].x
        trajectory_init.position.y = trajectory_init.position.y + TRAJECTORY_SCALE * trajectory.points[0].y
        # waypoints.append(copy.deepcopy(trajectory_init))
        larm.set_pose_target(trajectory_init)
        larm.go()

        count = 0
        for point in trajectory.points:
            wpose = copy.deepcopy(larm_init_pose)
            wpose.position.x = larm_init_pose.position.x + TRAJECTORY_SCALE * point.x
            wpose.position.y = larm_init_pose.position.y + TRAJECTORY_SCALE * point.y
            # waypoints.append(copy.deepcopy(wpose))
            # waypointが動かないのでset_pose_targetで 遅いので間引く
            count += 1
            print count
            if count % 10 == 0:
                print 'move'
                larm.set_pose_target(wpose)
                larm.go()
            

        # 最後も持ち上げる
        trajectory_end = copy.deepcopy(init_lift)
        trajectory_end.position.x = larm_init_pose.position.x + TRAJECTORY_SCALE * trajectory.points[-1].x
        trajectory_end.position.y = larm_init_pose.position.y + TRAJECTORY_SCALE * trajectory.points[-1].y
        #waypoints.append(copy.deepcopy(trajectory_end))
        larm.set_pose_target(trajectory_end)
        larm.go()

        print str(waypoints), '\n'

        # import ipdb; ipdb.set_trace()

        #(plan, fraction) = larm.compute_cartesian_path(waypoints, 0.01, 0.0)
    
        print "=" * 10, " move hand."
        #larm.execute(plan)
        # print str(plan), '\n'
        #rospy.sleep(plan.joint_trajectory.points[-1].time_from_start)
        #rospy.sleep(2)

    print "=" * 10, " Moving to an initial pose"
    larm.set_pose_target(larm_init_pose)
    larm.go()
    rospy.sleep(2)

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass


