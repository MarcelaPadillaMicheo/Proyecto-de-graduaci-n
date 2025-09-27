from Pololu3Pi import Pololu3Pi
import time

robot_id = 15
robot_ip = "192.168.50.115"

# Using agent_id to form the IP
# bot = Pololu3Pi()
# bot.connect(robot_id)   # builds 192.168.50.101
# bot.set_wheel_velocities(50, -50)
# time.sleep(5)
# bot.force_stop()
# bot.disconnect()

# Using IP directly
bot = Pololu3Pi()
bot.connect(ip=robot_ip)
bot.set_wheel_velocities(-75, 75)
time.sleep(5)
bot.force_stop()
bot.disconnect()