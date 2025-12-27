from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.db.models import Q, Max
from django.utils import timezone
from accounts.models import User
from .models import Conversation, Message, FirstContactTracker

@login_required
def inbox(request):
    """View all conversations"""
    # Get all conversations involving current user
    conversations = Conversation.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')
    
    # Calculate unread counts
    conv_list = []
    for conv in conversations:
        other_user = conv.get_other_user(request.user)
        unread = conv.unread_count(request.user)
        conv_list.append({
            'conversation': conv,
            'other_user': other_user,
            'unread_count': unread,
        })
    
    context = {
        'conversations': conv_list,
        'total_unread': sum(c['unread_count'] for c in conv_list),
    }
    return render(request, 'messaging/inbox.html', context)

@login_required
def conversation_view(request, user_id):
    """View conversation with a specific user"""
    other_user = get_object_or_404(User, pk=user_id)
    
    # Check if blocked
    from moderation.models import Block
    if Block.objects.filter(blocker=other_user, blocked=request.user).exists():
        django_messages.error(request, 'You cannot message this user.')
        return redirect('messaging:inbox')
    
    if Block.objects.filter(blocker=request.user, blocked=other_user).exists():
        django_messages.error(request, 'You have blocked this user.')
        return redirect('messaging:inbox')
    
    # Get or create conversation
    conversation = Conversation.objects.filter(
        Q(user1=request.user, user2=other_user) | 
        Q(user1=other_user, user2=request.user)
    ).first()
    
    if not conversation:
        # Ensure user1 is always the one with lower ID for consistency
        if request.user.id < other_user.id:
            conversation = Conversation.objects.create(user1=request.user, user2=other_user)
        else:
            conversation = Conversation.objects.create(user1=other_user, user2=request.user)
    
    # Mark messages as read
    Message.objects.filter(
        conversation=conversation,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)
    
    # Get messages
    conv_messages = conversation.messages.select_related('sender').all()
    
    # Check first contact status
    first_contact = FirstContactTracker.objects.filter(
        sender=request.user,
        receiver=other_user
    ).first()
    
    can_send = True
    message_limit_warning = None
    
    if first_contact and not first_contact.receiver_replied:
        if first_contact.message_count >= 3:
            can_send = False
            message_limit_warning = "You've reached the 3-message limit. Wait for them to reply."
        else:
            message_limit_warning = f"First contact: {first_contact.message_count}/3 messages sent. They must reply before you can send more."
    
    context = {
        'conversation': conversation,
        'other_user': other_user,
        'messages': conv_messages,
        'can_send': can_send,
        'message_limit_warning': message_limit_warning,
    }
    return render(request, 'messaging/conversation.html', context)

@login_required
def send_message(request, user_id):
    """Send a message to a user"""
    if request.method != 'POST':
        return redirect('messaging:conversation', user_id=user_id)
    
    other_user = get_object_or_404(User, pk=user_id)
    content = request.POST.get('content', '').strip()
    
    if not content:
        django_messages.error(request, 'Message cannot be empty.')
        return redirect('messaging:conversation', user_id=user_id)
    
    # Check if blocked
    from moderation.models import Block
    if Block.objects.filter(Q(blocker=other_user, blocked=request.user) | Q(blocker=request.user, blocked=other_user)).exists():
        django_messages.error(request, 'Cannot send message.')
        return redirect('messaging:conversation', user_id=user_id)
    
    # Get or create conversation
    conversation = Conversation.objects.filter(
        Q(user1=request.user, user2=other_user) | 
        Q(user1=other_user, user2=request.user)
    ).first()
    
    if not conversation:
        if request.user.id < other_user.id:
            conversation = Conversation.objects.create(user1=request.user, user2=other_user)
        else:
            conversation = Conversation.objects.create(user1=other_user, user2=request.user)
    
    # Check first contact limit
    first_contact, created = FirstContactTracker.objects.get_or_create(
        sender=request.user,
        receiver=other_user
    )
    
    if not first_contact.can_send_more:
        django_messages.error(request, 'You have reached the 3-message limit. Wait for them to reply.')
        return redirect('messaging:conversation', user_id=user_id)
    
    # Create message
    Message.objects.create(
        conversation=conversation,
        sender=request.user,
        receiver=other_user,
        content=content
    )
    
    # Update first contact tracker
    if not first_contact.receiver_replied:
        first_contact.message_count += 1
        first_contact.save()
    
    # Check if receiver has replied to sender
    reverse_tracker = FirstContactTracker.objects.filter(
        sender=other_user,
        receiver=request.user
    ).first()
    
    if reverse_tracker and not reverse_tracker.receiver_replied:
        reverse_tracker.receiver_replied = True
        reverse_tracker.save()
    
    conversation.updated_at = timezone.now()
    conversation.save()
    
    return redirect('messaging:conversation', user_id=user_id)

@login_required
def start_conversation(request):
    """Start a new conversation"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        try:
            other_user = User.objects.get(username=username)
            if other_user == request.user:
                django_messages.error(request, 'You cannot message yourself.')
                return redirect('messaging:inbox')
            return redirect('messaging:conversation', user_id=other_user.id)
        except User.DoesNotExist:
            django_messages.error(request, 'User not found.')
            return redirect('messaging:inbox')
    
    # Get all users except current user
    users = User.objects.exclude(id=request.user.id).order_by('username')
    return render(request, 'messaging/start_conversation.html', {'users': users})

@login_required
def group_chat(request, group_type):
    """View group chat (all members or admins only)"""
    if group_type not in ['all', 'admin']:
        django_messages.error(request, 'Invalid group type.')
        return redirect('messaging:inbox')
    
    # Check permissions
    if group_type == 'admin' and not request.user.is_admin:
        django_messages.error(request, 'You do not have access to admin chat.')
        return redirect('messaging:inbox')
    
    # Get messages
    group_messages = Message.objects.filter(
        is_group_message=True,
        group_type=group_type
    ).select_related('sender').order_by('created_at')
    
    context = {
        'group_type': group_type,
        'group_name': 'All Members' if group_type == 'all' else 'Admins Only',
        'messages': group_messages,
    }
    return render(request, 'messaging/group_chat.html', context)

@login_required
def send_group_message(request, group_type):
    """Send a group message"""
    if request.method != 'POST':
        return redirect('messaging:group_chat', group_type=group_type)
    
    if group_type not in ['all', 'admin']:
        django_messages.error(request, 'Invalid group type.')
        return redirect('messaging:inbox')
    
    # Check permissions
    if group_type == 'admin' and not request.user.is_admin:
        django_messages.error(request, 'You do not have access to admin chat.')
        return redirect('messaging:inbox')
    
    content = request.POST.get('content', '').strip()
    
    if not content:
        django_messages.error(request, 'Message cannot be empty.')
        return redirect('messaging:group_chat', group_type=group_type)
    
    # Create group message
    Message.objects.create(
        sender=request.user,
        content=content,
        is_group_message=True,
        group_type=group_type
    )
    
    return redirect('messaging:group_chat', group_type=group_type)

@login_required
def check_new_messages(request):
    """AJAX endpoint to check for new messages"""
    last_check = request.GET.get('last_check', 0)
    
    try:
        last_check = int(last_check)
    except:
        last_check = 0
    
    # Get total unread count
    total_unread = Message.objects.filter(
        receiver=request.user,
        is_read=False
    ).count()
    
    # Get new messages since last check (for current conversation if specified)
    user_id = request.GET.get('user_id')
    new_messages = []
    
    if user_id:
        try:
            other_user = User.objects.get(pk=user_id)
            conversation = Conversation.objects.filter(
                Q(user1=request.user, user2=other_user) | 
                Q(user1=other_user, user2=request.user)
            ).first()
            
            if conversation:
                messages_qs = conversation.messages.filter(
                    id__gt=last_check
                ).select_related('sender')
                
                for msg in messages_qs:
                    new_messages.append({
                        'id': msg.id,
                        'sender': msg.sender.username,
                        'sender_name': msg.sender.get_full_name() or msg.sender.username,
                        'content': msg.content,
                        'time': msg.created_at.strftime('%I:%M %p'),
                        'is_mine': msg.sender == request.user,
                    })
                
                # Mark as read
                conversation.messages.filter(
                    receiver=request.user,
                    is_read=False
                ).update(is_read=True)
        except:
            pass
    
    # Check group messages
    group_type = request.GET.get('group_type')
    if group_type in ['all', 'admin']:
        if group_type == 'all' or request.user.is_admin:
            group_messages_qs = Message.objects.filter(
                is_group_message=True,
                group_type=group_type,
                id__gt=last_check
            ).select_related('sender')
            
            for msg in group_messages_qs:
                new_messages.append({
                    'id': msg.id,
                    'sender': msg.sender.username,
                    'sender_name': msg.sender.get_full_name() or msg.sender.username,
                    'content': msg.content,
                    'time': msg.created_at.strftime('%I:%M %p'),
                    'is_mine': msg.sender == request.user,
                })
    
    return JsonResponse({
        'new_messages': new_messages,
        'total_unread': total_unread,
    })