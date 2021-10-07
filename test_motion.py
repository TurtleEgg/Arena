import sys
sys.path.append("/home/Code/Arena/")
sys.path.append("/home/Code/Arena/tests/")

from motion import Motion

motion = Motion(pos={"x": 0.25, "y": 0.75},
        t={"x": 1.0, "y": 0.0},
        vel={"x": 0.0, "y": 0.0},
        m_wheels={"right_wheel": 0.0, "left_wheel": 0.5})

motion.set_wheels({"right_wheel": 0.5, "left_wheel": 0.5})

for _ in range(10):
        motion.move(0.1)
        #print(motion.pos)

assert motion.pos["x"] - 0.4750000 < 0.0000000000000001
assert motion.pos["y"] - 0.75 < 0.0000000000000001

#motion2 = Motion()
#print(motion2.pos)