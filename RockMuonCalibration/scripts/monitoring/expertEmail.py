import smtplib
import email.mime
from email.Utils import formatdate
import os

def sendMail(fro, to, subject, text, server="localhost"):
  """ Sends an e-mail. """         
  msg = email.mime.Multipart.MIMEMultipart("mixed")
  msg['From'] = fro
  msg['To'] = to
  msg['Date'] = formatdate(localtime=True)
  msg['Subject'] = subject
  msg.attach( email.mime.Text.MIMEText(text) )
  smtp = smtplib.SMTP(server)
  smtp.sendmail(fro, to, msg.as_string() )
  smtp.close()



