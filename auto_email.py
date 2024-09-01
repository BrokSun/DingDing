import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


FROM_ADDR = 'email@address'
PSWD = 'pswd'
TO_ADDR = 'xxxxxx'
SMTP_SERVER = 'xxxxxx'


class EmailSender():
    def __init__(self, FROM_ADDR, TO_ADDR, PSWD, SMTP_SERVER):
        self.FROM_ADDR = FROM_ADDR
        self.TO_ADDR = TO_ADDR
        self.PSWD = PSWD
        self.SMTP_SERVER = SMTP_SERVER
        self.msg = None
    
    def add_content(self, text="", img_path="result.png"):
        content = MIMEText(text, "plain", "utf-8")
        self.msg = MIMEMultipart("related")
        self.msg.attach(content)

        img = MIMEImage(open(img_path, "rb").read())
        img.add_header("Content-Disposition", "attachment", filename=img_path)
        self.msg.attach(img)
    
    def send(self):
        self.msg['From'] = Header('Auto Signer')
        self.msg['To'] = Header('X')
        self.msg['Subject'] = Header("Auto Sign in Result", "utf-8")

        smtpobj = smtplib.SMTP_SSL(SMTP_SERVER)
        smtpobj.connect(SMTP_SERVER, 465)    
        smtpobj.login(FROM_ADDR, PSWD)   
        smtpobj.sendmail(FROM_ADDR, TO_ADDR, self.msg.as_string())

email_sender = EmailSender(FROM_ADDR, TO_ADDR, PSWD, SMTP_SERVER)