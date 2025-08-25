from django.shortcuts import render, get_object_or_404, redirect
from .models import Conversation
from django.contrib.auth.decorators import login_required
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
    user = request.user
    conversations = Conversation.objects.filter(participants=user).prefetch_related('messages', 'participants')
    
    unread_counts = {}
    for conv in conversations:
        count = conv.messages.exclude(sender=user).exclude(read_by=user).count()
        unread_counts[conv.id] = count
    
    context = {
        'conversations': conversations,
        'unread_counts': unread_counts,
        'user': user,
    }
    return render(request, 'chat_app/home.html', context)

@login_required
def chat_room(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user not in conversation.participants.all():
        return render(request, 'chat_app/access_denied.html')
    
    unread_messages = conversation.messages.exclude(read_by=request.user)
    for msg in unread_messages:
        msg.read_by.add(request.user)
    
    messages = conversation.messages.order_by('timestamp')
    return render(request, 'chat_app/chat.html', {
        'conversation': conversation,
        'messages': messages
    })

@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(participants=request.user)
    return render(request, 'chat_app/conversation_list.html', {'conversations': conversations})

@login_required
def create_group_conversation(request):
    if request.method == 'POST':
        group_name = request.POST.get('name')
        user_ids = request.POST.getlist('participants')

        if not group_name or not user_ids:
            return render(request, 'chat_app/create_group.html', {
                'error': "Nom du groupe et membres requis.",
                'users': User.objects.exclude(id=request.user.id)
            })

        conversation = Conversation.objects.create(is_group=True, name=group_name)
        conversation.participants.add(request.user)
        conversation.participants.add(*User.objects.filter(id__in=user_ids))

        return redirect('chat_app:chat_room', conversation_id=conversation.id)

    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat_app/create_group.html', {'users': users})

@login_required
def manage_group(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, is_group=True)

    if request.user not in conversation.participants.all():
        return render(request, 'chat_app/access_denied.html')

    if request.method == 'POST':
        user_ids = request.POST.getlist('participants')
        conversation.participants.set(User.objects.filter(id__in=user_ids))
        conversation.participants.add(request.user)
        messages.success(request, "Membres mis à jour.")
        return redirect('chat_app:chat_room', conversation_id=conversation.id)

    users = User.objects.exclude(id=request.user.id)
    current_members = conversation.participants.all()

    return render(request, 'chat_app/manage_group.html', {
        'conversation': conversation,
        'users': users,
        'current_members': current_members
    })