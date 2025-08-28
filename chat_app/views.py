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
    for conv in conversations:
        conv.unread_count = conv.messages.exclude(read_by=user).exclude(sender=user).count()

    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=user)
        unread_messages = conversation.messages.exclude(read_by=user)
        for msg in unread_messages:
            msg.read_by.add(user)
        messages = conversation.messages.order_by('timestamp')
    available_users = User.objects.exclude(id=user.id)
    total_unread = sum(conv.unread_count for conv in conversations)

    context = {
        'conversations': conversations,
        'conversation': conversation,
        'messages': messages,
        'available_users': available_users,
        'total_unread': total_unread,
    }
    return render(request, 'chat_app/home.html', context)

@login_required
@require_POST
def create_conversation(request):
    try:
        participant_ids = request.POST.getlist('participants')
        if not participant_ids:
            return JsonResponse({'success': False, 'error': 'Aucun participant sélectionné'})
        participant = get_object_or_404(User, id=participant_ids[0])
        existing_conv = Conversation.objects.filter(
            participants=request.user,
            is_group=False
        ).filter(
            participants=participant
        ).first()
        
        if existing_conv:
            return JsonResponse({
                'success': True, 
                'conversation_id': existing_conv.id
            })
        conversation = Conversation.objects.create(is_group=False)
        conversation.participants.add(request.user, participant)
        
        return JsonResponse({'success': True, 'conversation_id': conversation.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def create_group_conversation(request):
    try:
        group_name = request.POST.get('group_name')
        participant_ids = request.POST.getlist('participants')
        
        if not group_name or not participant_ids:
            return JsonResponse({'success': False, 'error': 'Nom du groupe et membres requis'})
        conversation = Conversation.objects.create(is_group=True, name=group_name)
        conversation.participants.add(request.user)
        participants = User.objects.filter(id__in=participant_ids)
        conversation.participants.add(*participants)
        
        return JsonResponse({'success': True, 'conversation_id': conversation.id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

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
@require_POST
def edit_message(request):
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        content = data.get('content')

        message = Message.objects.get(id=message_id, sender=request.user)
        message.content = content
        message.save()
        return JsonResponse({'success': True})
    except Message.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message non trouvé ou accès refusé.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required
@require_POST
def delete_message(request):
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')

        message = Message.objects.get(id=message_id, sender=request.user)
        message.delete()
        return JsonResponse({'success': True})
    except Message.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message non trouvé ou accès refusé.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_unread_notifications(request):
    user = request.user
    unread_conversations = []
    conversations = Conversation.objects.filter(participants=user)
    for conv in conversations:
        unread_count = conv.messages.exclude(read_by=user).exclude(sender=user).count()
        if unread_count > 0:
            if conv.is_group:
                name = conv.name
            else:
                name = ", ".join([p.username for p in conv.participants.exclude(id=user.id)])
            unread_conversations.append({
                'conversation_id': conv.id,
                'name': name,
                'unread_count': unread_count,
            })
    return JsonResponse({'notifications': unread_conversations})