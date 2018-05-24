#!/usr/bin/env python
# license removed for brevity
import rospy
import time
import pigpio # http://abyz.co.uk/rpi/pigpio/python.html
import struct
import threading
import signal
from std_msgs.msg import String
from Digital_Sensor_GPIO_Read import read_Sensor_GPIO
from Digital_Sensor_GPIO_Read import bubbleSort

# Which pin number to read (for example, on pi2Grover board this sonar is attached to D12/D13, which means GPIO pins 12 and 13)
# 	I then tested "12" and "13" as my RXD variable, the serial receive (RX) pin. Pin 12 gave no output when running it, Pin 13 gave me the "R#"
# 	which is the input we are looking to see from the Maxbotix sensor
RXD13=13
RXD19=19
RXD21=21

pi = pigpio.pi()

if not pi.connected:
   exit(0)

pigpio.exceptions = False # Ignore error if already set as bit bang read.

# Set baud rate here (From MaxBotix DataSheet: 9600, 8 bits, no parity, with one stop bit)
pi.bb_serial_read_open(RXD13, 9600, 8) 
pi.bb_serial_read_open(RXD19, 9600, 8) 
pi.bb_serial_read_open(RXD21, 9600, 8) 

pigpio.exceptions = True

# Invert line logic.
pi.bb_serial_invert(RXD13, 1) 
pi.bb_serial_invert(RXD19, 1) 
pi.bb_serial_invert(RXD21, 1) 

stop = time.time() + 60.0

rospy.init_node('Sonar_GPIO_Publish', anonymous=True)

class ThreadWorker(threading.Thread):
	
	def __init__(self, *args):
		super(ThreadWorker, self).__init__()
		self.pub = args[0]
		self.GPIO = args[1]
		self.stop = False
		#self.BasicPublishing(self.pub, self.GPIO)			# Has secret 3rd argument, which is self
		
	
	def BasicPublishing(self, pub, GPIO):
		rate = rospy.Rate(10) # 10hz
		while self.stop == False:
			if GPIO == 13:
				GPIO_Data_String = read_Sensor_GPIO(RXD13, pi)
			elif GPIO == 19:
				GPIO_Data_String = read_Sensor_GPIO(RXD19, pi)
			elif GPIO == 21:
				GPIO_Data_String = read_Sensor_GPIO(RXD21, pi)
			else:
				return
			print ('GPIO: ', GPIO)
			rospy.loginfo(GPIO_Data_String)
			pub.publish(GPIO_Data_String)
			rate.sleep()
		return

# Class From https://www.g-loaded.eu/2016/11/24/how-to-terminate-running-python-threads-using-signals/ 
class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass
 
# Funtion from https://www.g-loaded.eu/2016/11/24/how-to-terminate-running-python-threads-using-signals/
def service_shutdown(signum, frame):
    print('Caught signal %d' % signum)
    raise ServiceExit
    
pubRX13 = rospy.Publisher('Sonar_GPIO_13_Data', String, queue_size=10)
pubRX19 = rospy.Publisher('Sonar_GPIO_19_Data', String, queue_size=10)
pubRX21 = rospy.Publisher('Sonar_GPIO_21_Data', String, queue_size=10)

GPIO_13 = ThreadWorker(pubRX13, 13)
GPIO_19 = ThreadWorker(pubRX19, 19)
GPIO_21 = ThreadWorker(pubRX21, 21)

if __name__ == '__main__':
	
	# Register the signal handlers
	signal.signal(signal.SIGTERM, service_shutdown)
	signal.signal(signal.SIGINT, service_shutdown)
    
	try:
		GPIO_13_Pub_thread = threading.Thread(target = GPIO_13.BasicPublishing, args=[GPIO_13.pub, GPIO_13.GPIO])
		GPIO_19_Pub_thread = threading.Thread(target = GPIO_19.BasicPublishing, args=[GPIO_19.pub, GPIO_19.GPIO])
		GPIO_21_Pub_thread = threading.Thread(target = GPIO_21.BasicPublishing, args=[GPIO_21.pub, GPIO_21.GPIO])
		GPIO_13_Pub_thread.start()
		GPIO_19_Pub_thread.start()
		GPIO_21_Pub_thread.start()
		while True:
			time.sleep(0.5)
	except ServiceExit:
		print'STOPING'
		GPIO_13.stop = True
		GPIO_19.stop = True
		GPIO_21.stop = True
		
		#wait for shutdown
		GPIO_13_Pub_thread.join()
		GPIO_19_Pub_thread.join()
		GPIO_21_Pub_thread.join()
		
		# Close ports
		pi.bb_serial_read_close(RXD13)
		pi.bb_serial_read_close(RXD19)
		pi.bb_serial_read_close(RXD21)
		pi.stop()
		
		print'Closed Successfully'
		time.sleep(1)
	
	

