from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

@login_required
def chat_home(request):
    user = request.user
    conversation_id = request.GET.get('conversation_id')
    conversation = None
    messages = []

    conversations = Conversation.objects.filter(participants=user).prefetch_related('messages', 'participants')

    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=user)
        unread_messages = conversation.messages.exclude(read_by=user)
        for msg in unread_messages:
            msg.read_by.add(user)
        messages = conversation.messages.order_by('timestamp')

    context = {
        'conversations': conversations,
        'conversation': conversation,
        'messages': messages
    }
    return render(request, 'chat_app/home.html', context)

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

        return redirect(f"/chat/?conversation_id={conversation.id}")

    return render(request, 'chat_app/create_conversation.html')

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

        return redirect(f"/chat/?conversation_id={conversation.id}")

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
        return redirect(f"/chat/?conversation_id={conversation.id}")

    users = User.objects.exclude(id=request.user.id)
    current_members = conversation.participants.all()

    return render(request, 'chat_app/manage_group.html', {
        'conversation': conversation,
        'users': users,
        'current_members': current_members
    })

@login_required
@require_POST
def send_message(request):
    conversation_id = request.POST.get('conversation_id')
    content = request.POST.get('content')

    if not conversation_id or not content:
        return redirect('chat_app:chat_home')

    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)

    Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content
    )

    return redirect(f"/chat/?conversation_id={conversation_id}")

@csrf_exempt
@login_required
def edit_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Données JSON invalides.'})
        message_id = data.get('message_id')
        content = data.get('content')

        try:
            message = Message.objects.get(id=message_id, sender=request.user)
            message.content = content
            message.save()
            return JsonResponse({'success': True})
        except Message.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Message non trouvé ou accès refusé.'})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'})

@csrf_exempt
@login_required
def delete_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Données JSON invalides.'})
        message_id = data.get('message_id')

        try:
            message = Message.objects.get(id=message_id, sender=request.user)
            message.delete()
            return JsonResponse({'success': True})
        except Message.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Message non trouvé ou accès refusé.'})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'})
