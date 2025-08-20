from django.shortcuts import render, get_object_or_404
from .models import Conversation

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Conversation

@login_required
def chat_room(request, conversation_id):
    conversation = Conversation.objects.get(id=conversation_id)
    messages = conversation.messages.order_by('timestamp')

    return render(request, 'chat_app/chat.html', {
        'conversation': conversation,
        'messages': messages
    })

@login_required
def chat_home(request):
    conversation = Conversation.objects.filter(participants=request.user).first()
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user)

    return render(request, 'chat_app/home.html', {'conversation': conversation})

def chat_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    return render(request, 'chat_app/chat.html', {'conversation_id': conversation.id})