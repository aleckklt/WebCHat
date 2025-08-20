from django.shortcuts import render, get_object_or_404, redirect
from .models import Conversation
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation
from django.contrib.auth.models import User

@login_required
def create_conversation(request):
    if request.method == 'POST':
        other_username = request.POST.get('username')
        try:
            other_user = User.objects.get(username=other_username)
        except User.DoesNotExist:
            return render(request, 'chat_app/create_conversation.html', {'error': "Utilisateur introuvable."})
        conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=other_user,
            is_group=False
        ).first()

        if not conversation:
            conversation = Conversation.objects.create(is_group=False)
            conversation.participants.add(request.user, other_user)

        return redirect('chat_app:chat_room', conversation_id=conversation.id)

    return render(request, 'chat_app/create_conversation.html')

@login_required
def chat_home(request):
    conversations = Conversation.objects.filter(participants=request.user)
    return render(request, 'chat_app/home.html', {
        'conversations': conversations
    })

@login_required
def chat_room(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user not in conversation.participants.all():
        return render(request, 'chat_app/access_denied.html')    
    messages = conversation.messages.order_by('timestamp')
    return render(request, 'chat_app/chat.html', {
        'conversation': conversation,
        'messages': messages
    })

@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(participants=request.user)
    return render(request, 'chat_app/conversation_list.html', {'conversations': conversations})