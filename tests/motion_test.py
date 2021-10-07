import sys
sys.path.append("/home/Code/Arena/")
sys.path.append("/home/Code/Arena/tests/")

from motion import Motion

motion = Motion(pos={"x": 0.25, "y": 0.75},
        fi={"x": 0.0, "y": 0.0},
        vel={"x": 0.0, "y": 0.0},
        m_wheels={"right_wheel": 0.25, "left_wheel": 0.75})

print(motion.pos)
motion.move(0.1)
print(motion.pos)