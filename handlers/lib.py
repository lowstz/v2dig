#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import logging
import email
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import smtplib

# Toolkit
def encrypt_password(password):
    """Hash password on the fly."""
    m = hashlib.md5()
    m.update(password)
    password = m.hexdigest().upper()
    return password


def validate_password(hashed, input_password):
    return hashed == encrypt_password(input_password)


def send_mail(receiver,subject,plainText,htmlText,smtp_settings):
	
	msgRoot = MIMEMultipart('related')
	msgRoot['Subject'] = subject
	msgRoot['From'] = smtp_settings["email_address"]
	msgRoot['To'] = receiver

	# Encapsulate the plain and HTML versions of the message body in an
	# ‘alternative’ part, so message agents can decide which they want to display.
	msgAlternative = MIMEMultipart('alternative')
	msgRoot.attach(msgAlternative)

	msgText = MIMEText(plainText, 'plain', 'utf-8')
	msgAlternative.attach(msgText)

	msgText = MIMEText(htmlText, 'html', 'utf-8')
	msgAlternative.attach(msgText)

	# Send the message via local SMTP server.
	if smtp_settings["use_authentication"]:
		try:
			smtp = smtplib.SMTP_SSL(smtp_settings["server"],smtp_settings["ssl_port"])	
		except Exception as e:
			logging.exception(e)
			try:
				smtp = smtplib.SMTP_SSL(smtp_settings["server"],smtp_settings["tls_port"])
			except Exception as e:
				logging.exception(e)
				raise Exception
	else:
		smtp = smtplib.SMTP(smtp_settings["server"],smtp_settings["port"])
	smtp.login(smtp_settings["username"],smtp_settings["password"])
	# sendmail function takes 3 arguments: sender's address, recipient's address
	# and message to send - here it is sent as one string.
	smtp.sendmail(smtp_settings["email_address"], receiver, msgRoot.as_string())
	smtp.quit()
