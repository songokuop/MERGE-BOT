import os


class Config(object):
    API_HASH =("d28604398dc13af15dd108bb34a27a54")
    BOT_TOKEN = ("6305387154:AAG_2cjhpwqprlcGKMQsJ_G_EPOOhPkpdGk")
    TELEGRAM_API = ("7324525")
    OWNER = ("2116648189")
    OWNER_USERNAME = ("Mr_Haryanvi_Jaat")
    PASSWORD = ("MZ")
    DATABASE_URL = ("mongodb+srv://ROKU:ROKU@cluster0.nxjre0s.mongodb.net/?retryWrites=true&w=majority")
    LOGCHANNEL = ("--1002224821258")  # Add channel id as -100 + Actual ID
    GDRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", "root")
    USER_SESSION_STRING = ("BQGnLTcAceqwmovV1MXZGjZRx2PZWlrjKIAGj73wTmIjdPCbHxhx16RG53Z4PjJ6yVEKN4jT5_LU4wgna1KYrRbNd0DMB-FJzKNbkC1KEhjSs3THzD5dPK07jJABhKyYkvtD2iFy-HnjrrUw_3TapzajyFZwIWQ9V0LIC8BLtJ7klGoib-KPod_z7YUAN36wxECTipJfn8S9sgXn_cPxAaFiZQax0buGCg-H-LSqC5kO-p2uNaVX0hgr47kMmtd2qaxBtgaKBmP4PHG4pxlxU6QLQD2e4GJxNG7JoQZEIEKfQ0AMrVRdA-lSgLaOxX6aq8sf76w7OouUgQOcR1U2C2WyzKfCGwAAAABT3_5YAA")
    IS_PREMIUM = True
    START_PIC = ("https://telegra.ph/file/bb0690bfacfdc008ff788.jpg")
    MODES = ["video-video", "video-audio", "video-subtitle", "extract-streams"]
