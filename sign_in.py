import os
import time
import numpy as np

import calendar
import datetime
import logging

import base64
from PIL import Image, ImageFile

from msg import iyuu, TOKEN
from auto_email import email_sender
from ocr import Recognizer

# crucial app parameters
SIGN_IN_ACT = "-a android.intent.action.VIEW -d dingtalk://dingtalkclient/page/link?url=https://attend.dingtalk.com/attend/index.html"
HOME_ACT = "-n com.alibaba.android.rimet/com.alibaba.android.rimet.biz.LaunchHomeActivity"
STOP_APP = "com.alibaba.android.rimet"
# params
SMALL_INTERVAL = 10
LARGE_INTERVAL = 60
X = 550
Y = 1200
LOW = 1 * 60 # minutes
HIGH = 10 * 60 
MAX_RETRY = 3

# logging variables
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler('log.txt')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(console)

def wait(t):
    time.sleep(t)

def jump_to_activity(act):
    os.system("adb shell am start " + act)

def stop_app(app):
    os.system("adb shell am force-stop " + app)
    
def tap(x, y):
    os.system("adb shell input tap %d %d" % (x, y))
    
def power():
    os.system("adb shell input keyevent 26")

def swipe_unlock():
    os.system("adb shell input swipe 555 1500 555 200 500")

def random_wait(low, high):
    t = np.random.randint(low, high + 1)
    logger.info("Waiting %d secs before signing in..." % t)
    wait(t)

def screen_shot(save_path):
    os.system("adb exec-out screencap -p > " + save_path)

def compress_image(img_path, kb=200, quality=85, k=0.9):
    o_size = os.path.getsize(img_path) // 1024
    print(o_size, kb)
    if o_size <= kb:
        return
 
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    while o_size > kb:
        im = Image.open(img_path)
        x, y = im.size
        out = im.resize((int(x * k), int(y * k)), Image.ANTIALIAS)
        try:
            out.save(img_path, quality=quality)
        except Exception as e:
            print(e)
            break
        o_size = os.path.getsize(img_path) // 1024

def is_filtered(): # returns True if ignore [today]
    now = datetime.date.today() # system time
    day = calendar.weekday(now.year, now.month, now.day)

    # --- deprecated --- #
    # # filter national day
    # if now.month == 10 and 1 <= now.day <= 7:
    #     logger.info("Current datetime: %s -> %s. [国庆] Sign in skipped." % (str(now), calendar.day_name[day]))
    #     return True
    # elif now.month == 10 and now.day in (8, 9): # 调休
    #     return False
    # ------------------ #

    # normal - filter weekends
    if day > 4:
        logger.info("Current datetime: %s -> %s. Sign in skipped." % (str(now), calendar.day_name[day]))
        return True
    else:
        return False
    
def run():
    success = None
    # sign in procedure
    try:
        logger.info("Unlocking phone...")
        power() # unlock
        wait(SMALL_INTERVAL)
        swipe_unlock()
        wait(SMALL_INTERVAL)

        logger.info("Jumping to sign in activity...")
        jump_to_activity(SIGN_IN_ACT)
        wait(LARGE_INTERVAL)

        # --- verify content --- #
        logger.info("Verifying content...")
        screen_shot("result.png")
        wait(SMALL_INTERVAL)

        ocr = Recognizer()
        texts = ocr.read_text("result.png")
        verified = ocr.verify_content(texts, "上班打卡")
        if verified:
            logger.info("Verification passed.")
        else:
            raise RuntimeError("Content verification failed. Content:" + str(texts))
        # ---------------------- #

        logger.info("Signing in...")
        tap(X, Y)
        wait(SMALL_INTERVAL)
        
        logger.info("Taking screenshot...")
        screen_shot("result.png")
        wait(SMALL_INTERVAL)

        #logger.info("Returning to home...")
        #jump_to_activity(HOME_ACT)
        
        logger.info("Success!")
        success = True

    except Exception as e:
        logger.error(e.args)
        logger.error("Failed!")
        success = False
    
    finally:
        logger.info("Stopping app...")
        stop_app(STOP_APP)
        wait(SMALL_INTERVAL)

        power() # lock
        logger.info("Phone locked.")
        wait(SMALL_INTERVAL)
    
    return success

if __name__ == "__main__":
    skip = is_filtered()
    if skip is False:
        random_wait(LOW, HIGH) # randomize sign in timestamp

        for att in range(MAX_RETRY):
            logger.info("----- Attempt %d -----" % (att + 1))
            success = run()
            logger.info("----------------------")

            if success is True:
                break
    
    # # notification service #
    # log = ""
    # with open(file="log.txt", mode="r") as f:
    #     log += f.read()
    # # send screenshot - conditional send
    # if skip is False:
    #     email_sender.add_content(text=log, img_path="result.png")
    #     email_sender.send()
    # # send notification - send anyway
    # msg_sender = iyuu(TOKEN)
    # msg_sender("Auto Sign In", log)
    #
    # wait(1)
    # os.remove("log.txt")
