from django.contrib.auth.models import User 
from .models import AccountPages, Creds 
from .utils import get_all_accounts, get_long_lived_access_token
from django.core.mail import EmailMessage, get_connection, send_mail, send_mass_mail
from django.conf import settings 



def send_email_new_fb_page_save_failed(user, page, exception):
    """_summary_ 
    Send email to developer if the there are issue with saving 
    new Facebook pages created by the users. 
    """
    
    cred = Creds.objects.get(user=user)
    recipients_list = ['kundan.k.pandey02@gmail.com',]# "coboaccess@gmail.com"]
    message_body = f"""
    Unable to save new facebook page created from the users. 
    User info : 
    User Email : {user.email},
    User Id : {user.id} 
    ----------------------------
    
    Page info : 
    Page Name : {page['name']},
    Page Id   : {page['id']},
    ----------------------------
    
    Exception Raised : 
    {exception}
    """
    send_mail(
        "Error Saving new Facebook page from user.", 
        message_body, 
        settings.EMAIL_HOST_USER,
        recipients_list,
    )



def save_new_fb_pages():
    """_summary_
    capture all the new Facebook pages created by users and save 
    the relevent data in the db
    """
    creds = Creds.objects.all()
    for cred in creds: 
        user_access_token = cred.LONGLIVED_ACCESS_TOKEN
        user = cred.user
        page_ids = [page.page_id for page in AccountPages.objects.filter(user=user).all()]
        new_page_ids = get_all_accounts(user_access_token=user_access_token)
        for npi in new_page_ids:
            if npi['id'] not in page_ids:
                print(npi['id'])
                print(f"{npi['name']} is not in the db.")
                print()
                page = AccountPages()
                page.user = user 
                page.page_access_token = npi['access_token']
                page.page_id = npi['id']
                page.page_name = npi['name']
                try: 
                    page.longlived_access_token = get_long_lived_access_token(
                                                            api_key=cred.APP_ID, 
                                                            # api_key="",
                                                            api_secret=cred.APP_SECRET, 
                                                            access_token=npi['access_token']
                                                            )
                    print("Longlived page access token : ", page.longlived_access_token)
                    page.has_access_token = True 
                    page.save()
                except Exception as e : 
                    send_email_new_fb_page_save_failed(user=user, page=npi, exception=e)
                