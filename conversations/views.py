from django.shortcuts import render

import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from facebook.models import AccountPages as FacebookPage
from .models import Conversation
from .email import send_conversation_email
# Create your views here.

def home(request):
    return render(request, "conversations/index.html")


@csrf_exempt
def facebook_webhook(request):
    if request.method == 'GET':
        # Verification challenge response
        verify_token = 'this_is_webhook_conversations_token'
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode and token:
            if mode == 'subscribe' and token == verify_token:
                return HttpResponse(challenge, status=200)
            else:
                return HttpResponse('Forbidden', status=403)

    elif request.method == 'POST':
        # Handle incoming messages
        data = json.loads(request.body)
        send_conversation_email(json_data=data)
        if 'entry' in data:
            for entry in data['entry']:
                if 'messaging' in entry:
                    for message_event in entry['messaging']:
                        if 'message' in message_event:
                            page_id = message_event['recipient']['id']
                            sender_id = message_event['sender']['id']
                            message_text = message_event['message']['text']
                            timestamp = message_event['timestamp']

                            # Find the FacebookPage instance
                            try:
                                page = FacebookPage.objects.get(page_id=page_id)
                            except FacebookPage.DoesNotExist:
                                continue

                            # Create a new Conversation
                            Conversation.objects.create(
                                page=page,
                                conversation_id=message_event['message']['mid'],
                                sender_id=sender_id,
                                message=message_text,
                                created_time=timestamp
                            )
        return JsonResponse({'status': 'success'}, status=200)

    return JsonResponse({'status': 'invalid method'}, status=400)
