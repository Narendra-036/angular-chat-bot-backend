from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import  JsonResponse
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *


@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            auth_login(request, user)  # Create session
            return JsonResponse({'status': 'success',
                                 'user': {
                                     'id': user.id,
                                     'username': user.username,
                                     'email': user.email
                                 },
                                 'message': 'Login Successfully'}, safe=False)
        else:
            return JsonResponse({'status': 'failed', 'message': 'Invalid credentials'}, status=400)
    
    return JsonResponse({'status': 'failed', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'status': 'success',
                                 'message': 'User Registered Successfully'}, safe=False, status=201)
        else:
            return JsonResponse({'status': 'failed', 'errors': serializer.errors}, status=400)
    
    return JsonResponse({'status': 'failed', 'message': 'Invalid request method'}, status=400)





@login_required
@csrf_exempt
def chat_intiate(request):
    room = Room.objects.create(user=request.user)
    return JsonResponse({'status': 'success',
                         'room': {
                             'id': room.id,
                             'slug': room.slug
                         },
                         'message': 'Chat Room Created Successfully'}, safe=False)

@csrf_exempt
def chat_room(request, slug):
    room = get_object_or_404(Room, slug=slug)
    messages = Messeges.objects.filter(room=room)
    messages_data = MessegesSerializer(messages, many=True).data
    
    return JsonResponse({'status': 'success',
                         'room': {
                             'id': room.id,
                             'slug': room.slug
                         },
                         'messages': messages_data,
                         'message': 'Chat Room Found Successfully'}, safe=False)

    
@csrf_exempt
@login_required
def send_message(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        try:
            room = Room.objects.get(slug=data['slug'])
        except Room.DoesNotExist:
            return JsonResponse({'status': 'failed', 'message': 'Room not found'}, status=404)

        message_text = data.get('message')
        if not message_text:
            return JsonResponse({'status': 'failed', 'message': 'Message cannot be empty'}, status=400)

        message = Messeges.objects.create(user=request.user, room=room, messege=message_text)

        bot_reply = f"Hello, How can I help you, {request.user.username}?"
        bot_user = User.objects.get(username='bot')
        reply = Messeges.objects.create(user=room.user, room=room, messege=bot_reply)
        
        return JsonResponse({'status': 'success',
                             'message': 'Message Sent Successfully',
                             'user_message': message.messege,
                             'bot_reply': reply.messege}, safe=False)
    return JsonResponse({'status': 'failed', 'message': 'Invalid request method'}, status=400)



@csrf_exempt
def logout(request):
    auth_logout(request)  # This clears the session
    return JsonResponse({'status': 'success',
                         'message': 'Logged out successfully'}, safe=False)
