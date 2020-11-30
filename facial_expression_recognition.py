#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

""" nao机器人表情识别程序 """

import qi
import argparse
import sys
import time
from PIL import Image
import socket


def main(session):
    """
    此程序从机器人获取图片后传到服务端 nao_Fer_server/Fer_server_2.py ，识别表情后将结果传回此程序，机器人再做出反应
    """
    # 唤醒机器人
    # Get the service ALMotion.

    motion_service = session.service("ALMotion")

    motion_service.wakeUp()

    # 机器人识别并跟踪人脸
    face_detection = session.service("ALFaceDetection")
    memory = session.service("ALMemory")
    tts = session.service("ALTextToSpeech")

    # Get the services ALBasicAwareness

    ba_service = session.service("ALBasicAwareness")
    ba_service.setEnabled(True)
    ba_service.setStimulusDetectionEnabled("People", True)
    ba_service.setStimulusDetectionEnabled("Touch", False)
    ba_service.setStimulusDetectionEnabled("Sound", False)
    ba_service.setStimulusDetectionEnabled("Movement", False)
    ba_service.setTrackingMode("Head")
    ba_service.setEngagementMode("FullyEngaged")
    # Subscribe to the ALFaceDetection proxy
    # This means that the module will write in ALMemory with
    # the given period below
    period = 500
    face_detection.subscribe("Test_Face", period, 0.0)

    try:
        while True:
            time.sleep(5)
            memValue = "FaceDetected"
            val = memory.getData(memValue)
            if val and isinstance(val, list) and len(val) == 5:
                faceInfoArray = val[1]
                print faceInfoArray
                if faceInfoArray and len(faceInfoArray) == 2:
                    tts.say("你好")
                    time.sleep(1)
                    recognition()
                    # motion_service.setIdlePostureEnabled("Body", True)
    except KeyboardInterrupt:
        face_detection.unsubscribe("Test_Face")
        ba_service.setEnabled(False)
        motion_service.rest()


def recognition():
    # Get the service ALVideoDevice.

    video_service = session.service("ALVideoDevice")
    resolution = 2  # 2:VGA,640x480像素    3:1280x960px   4:2560x1920px
    colorSpace = 11  # RGB

    videoClient = video_service.subscribe("python_client", resolution, colorSpace, 5)

    t0 = time.time()

    # Get a camera image.
    # image[6] contains the image data passed as an array of ASCII chars.
    naoImage = video_service.getImageRemote(videoClient)

    t1 = time.time()

    # Time the image transfer.
    print "acquisition delay ", t1 - t0

    video_service.unsubscribe(videoClient)

    # Now we work with the image returned and save it as a PNG  using ImageDraw
    # package.

    # Get the image size and pixel array.
    imageWidth = naoImage[0]
    imageHeight = naoImage[1]
    array = naoImage[6]
    image_string = str(bytearray(array))

    # Create a PIL Image from our pixel array.
    im = Image.frombytes("RGB", (imageWidth, imageHeight), image_string)

    # Save the image.
    im.save("camImage.png", "PNG")
    # im.show()
    print '照片已生成'

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建 socket 对象
    host = '192.168.1.9'  # 获取本地主机名
    port = 12345  # 设置端口号
    s.connect((host, port))
    s.send("照片已生成")

    animSpeech = session.service("ALAnimatedSpeech")
    emotion = s.recv(1024).decode()

    if emotion == 'no face':
        animSpeech.say(" ^start(animations/Stand/Exclamation/NAO/Center_Neutral_EXC_04) 对不起，我没能检测到人脸"
                       " ^wait(animations/Stand/Exclamation/NAO/Center_Neutral_EXC_04)")
    elif emotion == 'angry':
        animSpeech.say("^start(animations/Stand/Gestures/Shocked_1) 你看起来很生气 ^wait(animations/Stand/Gestures/Shocked_1)")
        animSpeech.say("^start(animations/Stand/Gestures/CalmDown_3) 请冷静下来 ^wait(animations/Stand/Gestures/CalmDown_3)")
    elif emotion == 'disgust':
        animSpeech.say(" ^start(animations/Stand/Question/NAO/Center_Neutral_QUE_01) 你的表情看起来是厌恶，我说的对吗？"
                       " ^wait(animations/Stand/Question/NAO/Center_Neutral_QUE_01) ")
    elif emotion == 'fear':
        animSpeech.say(" ^start(animations/Stand/Question/NAO/Center_Neutral_QUE_03) 你看起来很恐惧，怎么了？"
                       " ^wait(animations/Stand/Question/NAO/Center_Neutral_QUE_03)")
    elif emotion == 'happy':
        animSpeech.say(" ^start(animations/Stand/Exclamation/NAO/Center_Neutral_EXC_01) 你看起来很开心"
                       " ^wait(animations/Stand/Exclamation/NAO/Center_Neutral_EXC_01) ")
        animSpeech.say(" ^start(animations/Stand/Gestures/Happy_1) 我也很开心 ^wait(animations/Stand/Gestures/Happy_1) ")
    elif emotion == 'sad':
        animSpeech.say(" ^start(animations/Stand/Gestures/Sad_2) 别伤心 ^wait(animations/Stand/Gestures/Sad_2) ")
        animSpeech.say(" ^start(animations/Stand/Gestures/AirJuggle_1) 我可以让你高兴起来！ "
                       " ^wait(animations/Stand/Gestures/AirJuggle_1) ")
    elif emotion == 'surprise':
        animSpeech.say(" ^start(animations/Stand/Gestures/Surprised_1) 为什么你看起来这么惊讶？发生了什么？"
                       " ^wait(animations/Stand/Gestures/Surprised_1) ")
    elif emotion == 'neutral':
        animSpeech.say(" ^start(animations/Stand/Affirmation/NAO/Center_Neutral_AFF_04) 你的表情是中立的 "
                       " ^wait(animations/Stand/Affirmation/NAO/Center_Neutral_AFF_04) ")
    else:
        animSpeech.say(" ^start(animations/Stand/Exclamation/NAO/Center_Neutral_EXC_04) 对不起，我没能识别你的表情"
                       " ^wait(animations/Stand/Exclamation/NAO/Center_Neutral_EXC_04)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.1.11",
                        help="Robot IP address. On robot or Local Naoqi: use '192.168.1.11'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) + ".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session)
