# coding=utf-8
import socket
import time
from naoqi import ALProxy


# Replace this with your robot's IP address
IP = "192.168.1.10"
PORT = 9559
address = ('192.168.1.8', 49516)

# Create a proxy to ALPhotoCapture
try:
    photoCaptureProxy = ALProxy("ALPhotoCapture", IP, PORT)
except Exception, e:
    print "Error when creating ALPhotoCapture proxy:"
    print str(e)
    exit(1)
else:
    photoCaptureProxy.setResolution(2)
    photoCaptureProxy.setPictureFormat("png")


def take_photos():

    photo = photoCaptureProxy.takePicture("/home/nao/recordings/cameras/", "image")
    send(photo[0])


def send(photo):
    print 'sending {}'.format(photo)
    data = read_file(photo)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    sock.sendall('{}|{}'.format(len(data), photo[0]))
    reply = sock.recv(1024)
    print 'reply:{}'.format(reply)
    if reply == 'got size and filename':
        sock.sendall(data)
        reply2 = sock.recv(1024)
        print 'reply2:{}'.format(reply2)
        if reply2 == 'got image':
            print '已发送{}'.format(photo[0])


def read_file(photo):
    try:
        photo_file = open(photo, 'rb')
        data = photo_file.read()
    except IOError:
        print '读取{}失败'.format(photo)
    else:
        photo_file.close()
        return data


if __name__ == '__main__':
    take_photos()

