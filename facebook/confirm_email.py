from django.contrib.auth.models import User 
from .models import Creds
from django.shortcuts import render, redirect 
from django.http import HttpResponse



def confirm_email(request):
    if request.method == 'POST':
        emails = request.POST.getlist('email[]')
        confirm_emails = request.POST.getlist('confirm_email[]')

        # Perform any additional validation here if required

        # Assuming you have an Email model to save the emails
        # from .models import Email
        for email, confirm_email in zip(emails, confirm_emails):
            # email_obj = Email(email=email, confirm_email=confirm_email)
            # email_obj.save()
            print(email, confirm_email)
        # Redirect to a success page or another URL after saving
        return HttpResponse("success!")
    return render(request, "facebook_accounts/confirm_email.html", {})




def save_emails(request):
    if request.method == 'POST':
        emails = request.POST.getlist('email[]')
        confirm_emails = request.POST.getlist('confirm_email[]')

        # Perform any additional validation here if required

        # Assuming you have an Email model to save the emails
        from .models import Email
        for email, confirm_email in zip(emails, confirm_emails):
            email_obj = Email(email=email, confirm_email=confirm_email)
            email_obj.save()

        # Redirect to a success page or another URL after saving
        return redirect('success_page')

    return render(request, 'template_name.html')
