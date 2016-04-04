import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


def send_mail(send_from, send_to, subject, text, files=None,
              server="smtp.gmail.com"):
#     assert isinstance(send_to, list)

    print files
    gmail_user = 'punit.vanjani@gmail.com'
    gmail_pwd = 'punit82647899'

    msg = MIMEMultipart(
        From=send_from,
#         To=COMMASPACE.join(send_to),
        To=send_to,
        Date=formatdate(localtime=True),
        Subject=subject
    )
    msg.attach(MIMEText(text))

#     for f in files or []:
#         print f
#         with open(f, "r") as fil:
#             msg.attach(MIMEApplication(
#                 fil.read(),
#                 Content_Disposition='attachment; filename="%s"' % basename(f),
#                 Name=basename(f)
#             ))
#     with open(files, "r") as fil:
#         msg.attach(MIMEApplication(
#             fil.read(),
#             Content_Disposition='attachment; filename="%s"' % basename(f),
#             Name=basename(files)
#         ))
    smtp = smtplib.SMTP(server,587)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo
    smtp.login(gmail_user, gmail_pwd)
    smtp.sendmail(send_from, send_to, msg.as_string())
    print 'done!'
    smtp.close()