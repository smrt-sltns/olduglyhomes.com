from celery import Celery, shared_task
from django.conf import settings 
from django.core.mail import EmailMessage, get_connection, send_mail, send_mass_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.template.loader import render_to_string

from datetime import timezone 
import datetime 
import time
import os
import json
import urllib.request
import smtplib

# from automation.models import LogNegativeComments, LogPositiveComments
from .myads_utils import (
        save_comments, negative_comment_today, 
        comment_count_in_ad, save_campaings, 
        save_ads)

#emails logic for every 2 hours and every day 

def negative_comments_send_email(user_email, file_name):
    data = negative_comment_today(file_name)
    if len(data["new_negative_comments"]) != 0:
        new_negative_comments = data['new_negative_comments']
        ignore_comment_list = json.loads(
            open("JSON/ignored_comments.json", "r").read()
            )
        new_comments = data['new_negative_comments']
        old_comments = data['old_negative_comments']
        msg_html = render_to_string('email_template/negative_comments.html', 
                                    {'new_negative_comments': new_comments, "old_negative_comments": old_comments})
        try:
            send_mail(
                'email title',
                "Negative comments!",
                settings.EMAIL_HOST_USER,
                # ['kundan.k.pandey02@gmail.com', "georgeyoumansjr@gmail.com","coboaccess2@gmail.com"],
                [user_email,],
                html_message=msg_html,)
            mail_sent = True
            print("MAIL SENT. Negative comments today.\nThese comments will be ignore in next batch!")
        except smtplib.SMTPException as e:
            mail_sent = False
        except Exception as e:
            mail_sent = False
        #ignore the comment once it is sent 
        new_com = [c['comment_id'] for c in data['new_negative_comments']]
        old_com = [c['comment_id'] for c in data['old_negative_comments']]
        new_com.extend(old_com)
        ignore_comment_list.extend(new_com)
        json_obejct  = json.dumps(ignore_comment_list, indent=4)
        with open("JSON/ignored_comments.json", "w") as j_file: # ignored comments list 
            j_file.write(json_obejct)
        # mail_sent = True 
    else:
        print('NO MAIL SENT! Negative comments.')
        mail_sent = False
        new_negative_comments = []
    return (mail_sent, new_negative_comments)

# user email should a list coming from email models 
def positive_comments_send_email(user_email, file_name):
    data = comment_count_in_ad(file_name)
    if len(data) != 0:
        msg_html = render_to_string('email_template/positive_comments.html', 
                                    {'data': data})
        try: 
            send_mail(
                'Total comment made yesterday!',
                "Comments made yesterday!",
                settings.EMAIL_HOST_USER,
                [user_email,],
                # ['kundan.k.pandey02@gmail.com',
                # "georgeyoumansjr@gmail.com", 
                # "coboaccess2@gmail.com"],
                html_message=msg_html,
            )
            print("MAIL SENT! Positive comments yesterday!")
            mail_sent = True
        except Exception as e:
            mail_sent = False
    else:
        print("NO MAIL SENT! Positive comments.")
        mail_sent = False
        data = []
    return (mail_sent, data)



#<<<<=================================================================================================================>>>>
#currently not in use 

# @shared_task()
def send_email():  
    with get_connection(  
        host=settings.EMAIL_HOST, 
    port=settings.EMAIL_PORT,  
    username=settings.EMAIL_HOST_USER, 
    password=settings.EMAIL_HOST_PASSWORD, 
    use_tls=settings.EMAIL_USE_TLS  
    ) as connection:  
        subject = "Welcome to our community! 🍚 Your 10 Delicious Rice Recipes are attached below!"
        email_from = settings.EMAIL_HOST_USER  
        # recipient_list = json.load(open('JSON/emails.json', 'r'))['new_email']
        recipient_list = ["kundanpandey.dev@gmail.com", "kundan.k.pandey03@gmail.com","kundan.k.pandey02@gmail.com" ]   
        if len(recipient_list) != 0:

            html_content = open("template/email.html").read()
            pdf_file = open("template/GER Document.pdf", 'rb').read()
            mass_email_message = [] 
            for recipient in recipient_list:
                email = EmailMessage(subject, html_content, email_from, [recipient], connection=connection)
                email.content_subtype = "html"
                email.attach("GER Document.pdf", pdf_file) 
                mass_email_message.append(email)

            connection.send_messages(mass_email_message)
            print(recipient_list)
            print('Mail sent to above list of mails.')
        else:
            print("NO NEW LEADS FOUND!")


# make a call every 5 minutes and see if there are any new users
def get_all_leads(file_path='JSON/data.json',token=""):
    ads_id = "723940182548849"
    all_leads = f"https://graph.facebook.com/{ads_id}/leads?access_token={token}"
    leads_object = json.loads(urllib.request.urlopen(all_leads).read())    
    json_object = json.dumps(leads_object)
    json_file = open('JSON/data.json', 'w', encoding='utf-8')
    json_file.write(json_object)
    json_file.close() 
    time.sleep(3)  
    # <==============================>


def intersection(test_list, remove_list):
    res = [i for i in test_list if i not in remove_list]
    return res



def store_email_to_json(file_path="JSON/data.json"):
    email_dir = {}
    email_list = []
    with open(file_path, 'r', encoding='utf-8') as json_file:
        file_data = json.load(json_file)
    print(len(file_data['data']))
    for d in file_data['data']:
        for n in d['field_data']:
            if n['name'] == 'email':
                # print(n['values'])
                email = n['values']
                email_list.extend(email)
    print(len(email_list))
    email_dir["email"] = email_list # store the email from the current leads 
    old_email_json = open("JSON/emails.json", "r+", encoding='utf-8') # read the existing email.json
    old_email_data = json.load(old_email_json)
    new_email = intersection(email_dir['email'], old_email_data['email'])
    print(new_email)
    print(len(new_email))
    email_dir['new_email'] = new_email

    email_json = open('JSON/emails.json', 'w', encoding='utf-8')
    json_obejct = json.dumps(email_dir, indent=4)
    email_json.write(json_obejct)
    email_json.close()

