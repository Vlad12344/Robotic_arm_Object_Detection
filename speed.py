# from pulseapi import RobotPulse, position, PulseApiException, pose, MotionStatus, MT_LINEAR, tool_info, tool_shape, \
#     Point, create_simple_capsule_obstacle
# import math
#
# robot = RobotPulse('10.10.10.20:8081')
#
# home_pose = pose([0, -90, 0, -90, -90, 0])
# robot.set_pose(home_pose, speed=30)
# # position_targets = [
# #     position([-0.4, -0.5, 0.25], [math.pi, 0, 0]),
# #     position([-0.4, 0.5, 0.25], [math.pi, 0, 0]),
# # ]
# # for i in range(5):
# #     robot.run_positions(position_targets, tcp_max_velocity=0.5, motion_type=MT_LINEAR)
# #
# #
