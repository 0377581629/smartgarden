from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import boto3
from boto3.dynamodb.conditions import Key, Attr
import jsonconverter as jsonc
import serial
from time import sleep

# Get serial to fetch data from arduino
ser = serial.Serial('/dev/ttyUSB0', 9600)

def customCallback(client, userdata, message):
	print("Received a new message: ")
	print(message.payload)
	print("from topic: ")
	print(message.topic)
	print("--------------\n\n")

# https://s3.amazonaws.com/aws-iot-device-sdk-python-docs/sphinx/html/index.html
host = "a290uc2ksy4m1j-ats.iot.us-west-2.amazonaws.com"
rootCAPath = "/home/pi/Templates/Project/smartgarden/rootca.pem"
certificatePath = "/home/pi/Templates/Project/smartgarden/certificate.pem.crt"
privateKeyPath = "/home/pi/Templates/Project/smartgarden/private.pem.key"

my_rpi = AWSIoTMQTTClient("basicPubSub")
my_rpi.configureEndpoint(host, 8883)
my_rpi.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

my_rpi.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
my_rpi.configureDrainingFrequency(2)  # Draining: 2 Hz
my_rpi.configureConnectDisconnectTimeout(10)  # 10 sec
my_rpi.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
my_rpi.connect()
my_rpi.subscribe("smartgarden/status", 1, customCallback) #https://www.hivemq.com/blog/mqtt-essentials-part-6-mqtt-quality-of-service-levels/
sleep(2)

# Publish to the same topic in a loop forever
loopCount = 0
while True:
  dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
  table = dynamodb.Table('SmartGarden_status')

  response = table.query(KeyConditionExpression=Key('id').eq('id_status'),
      ScanIndexForward=False
  )

  items = response['Items']

  n=1
  data = items[:n]
  uStatus = data[0]['status']
  status = uStatus.encode('latin-1')
  print(status)
  ser.write(status)
  sleep(4)
