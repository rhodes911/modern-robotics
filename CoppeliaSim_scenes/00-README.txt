This folder contains CoppeliaSim simulation scenes associated with the book "Modern Robotics: Mechanics, Planning, and Control," Kevin Lynch and Frank Park, Cambridge University Press, 2017.

To learn more about the book, the associated software, CoppeliaSim simulation, book videos, Coursera courses, etc., see
 
https://modernrobotics.org

For a more detailed description of the CoppeliaSim demonstration scenes, see

https://hades.mech.northwestern.edu/index.php/CoppeliaSim_Introduction

Authors: Huan Weng, Jarvis Schultz, and Kevin Lynch

Version history:

November 2024.
Modified to comment out unnecessary writes-to-file causing run-time errors on Mac OS.

November 2019.
Minor bug corrections.

August 2018.
Original version.

=====
 
Below is a brief description of the files.  The CoppeliaSim scenes all end in .ttt.

Scene1_UR5.ttt: CoppeliaSim scene for interactive manipulation of the UR5 six-joint robot.

Scene2_UR5_csv.ttt:  CoppeliaSim scene that animates the UR5 to follow a path specified in a file.

Scene2_example.csv:  An example input file for Scene2_UR5_csv.ttt.

Scene3_youBot.ttt:  CoppeliaSim scene for interactive manipulation of the youBot mobile manipulator, consisting of an omnidirectional mecanum-wheel mobile base and a five-joint robot arm.

Scene4_youBot_csv.ttt:  CoppeliaSim scene that animates the youBot to follow a path specified in a file.

Scene4_example.csv:  An example input file for Scene4_youBot_csv.ttt.

Scene4_base_motions:  A folder containing input files for Scene4_youBot_csv.ttt that only move the mobile base, to demonstrate the motion of the mecanum wheels when the mobile base undergoes certain basic motions:
  yb1.csv:  Mobile base spins in place at constant speed.
  yb2.csv:  Mobile base moves forward at constant speed.
  yb3.csv:  Mobile base moves sideways at constant speed.
  yb4.csv:  Mobile base moves diagonally at constant speed.
  yb5.csv:  Mobile base moves along another diagonal at constant speed.

Scene5_motion_planning.ttt:  CoppeliaSim scene that animates a planar mobile robot moving along a graph representation of a cluttered planar C-space.

Scene5_example:  A folder containing example input files needed by Scene5_motion_planning.ttt:
  nodes.csv:  The nodes in the graph.
  edges.csv:  The edges in the graph.
  path.csv:  The solution path.
  obstacles.csv:  The circular obstacles.

Scene6_youBot_cube.ttt:  CoppeliaSim scene animating solutions to the youBot manipulating a cube.

Scene6_example.csv:  An example input file for Scene6_youBot_cube.ttt.

Scene7_MTB_csv.ttt:  CoppeliaSim scene that animates a path for a four-joint RRPR robot.

Scene7_example.csv:  An example input file for Scene7_MTB_csv.ttt.

Scene8_gripper_csv.ttt:  CoppeliaSim scene that animates a path for the end-effector (gripper) of the youBot.  This is used to verify youBot end-effector reference trajectories without requiring the full motion of the youBot.

Scene8_example.csv:  An example input file for Scene8_gripper_csv.ttt.


 
