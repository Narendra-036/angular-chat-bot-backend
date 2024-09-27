from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import  JsonResponse
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
import json
import datetime



@csrf_exempt
def login(request):
    if request.method == 'POST':
        
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            if not email or not password:
                return JsonResponse({'error': 'All fields are required'}, status=400)
            if not User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'User not found'}, status=404)
            else: 
                user = User.objects.get(email=email)
                if user.check_password(password):
                    return JsonResponse({'status': 'success'}, status=200)
                
                return JsonResponse({'error': 'Invalid credentials'}, status=400)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'status': 'failed', 'message': 'Invalid request method'}, status=400)



@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            fullname = data.get('full_name')
            email = data.get('email')
            password = data.get('password')
            username = fullname.replace(' ', '_').lower()
            
            optional_fields = {key: data[key] for key in data if key not in ['full_name', 'email', 'password']}
            quick_signup = optional_fields.get('quick_signup', False)
            provider_platform = optional_fields.get('provider_platform', None)
            
            if quick_signup:
                if User.objects.filter(email=email).exists():
                    return JsonResponse({'messege': 'User registered successfully!'}, status=201)


            if not username or not email or not password:
                return JsonResponse({'error': 'All fields are required'}, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)
                        
            user = User.objects.create(username=username, email=email, password=password, fullname=fullname, quick_signup=quick_signup, provider_platform=provider_platform)
            user.save()
            return JsonResponse({'message': 'User registered successfully!'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)



@csrf_exempt
def chathome(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            user_data = User.objects.get(email=email)
            rooms = user_data.user_rooms.all()
            user_data = UserSerializer(user_data).data
            return JsonResponse({
                    'status': 'success',
                    'user': user_data, 
                    'rooms': RoomSerializer(rooms, many=True).data,
                    'message': 'User Found Successfully'
                }, safe=False)
                
            
        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'status': 'failed', 'message': 'Invalid request method'}, status=400)



@csrf_exempt
def chat_intiate(request):
    if request.method == 'POST':
        try:
            print("Request Body:", request.body)
            data = json.loads(request.body)
            email = data.get('email')
            if not email:
                return JsonResponse({'error': 'Email is required'}, status=400)
            user = User.objects.get(email=email)
            username = user.fullname.split(' ')[0]  
            room_name = f"{username}-{datetime.datetime.now().date()}-{datetime.datetime.now().time()}"
            room = Room.objects.create(name=room_name)
            room.user.add(user)
            bot_user, _ = User.objects.get_or_create(
                username='bot', 
                defaults={'email': 'bot@angularbot.com', 'fullname': 'Angular Bot'}
            )
            
            messege = Messeges.objects.create(user=bot_user, room=room, message="Hello, How can I help you?")
            messege.save()
            
            room.user.add(bot_user)
            room.save()
            room_data = RoomSerializer(room).data
            
            
            
            return JsonResponse({
                'status': 'success',
                'room': {
                    'room_data': room_data,
                    'slug': room.slug
                },
                'message': 'Chat Room Created Successfully'
            }, safe=False)

        except User.DoesNotExist:
            return JsonResponse({'error': 'User with this email does not exist'}, status=404)

        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'status': 'failed', 'message': 'Invalid request method'}, status=400)



@csrf_exempt
def chat_room(request, slug):
    room = get_object_or_404(Room, slug=slug)
    messages = Messeges.objects.filter(room=room)
    messages_data = MessegesSerializer(messages, many=True).data
    
    return JsonResponse({'status': 'success',
                         'room': {
                             'slug': room.slug
                         },
                         'messages': messages_data,
                         'message': 'Chat Room Found Successfully'},
                        safe=False)


@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        try:
            room = Room.objects.get(slug=data['room_slug'])
        except Room.DoesNotExist:
            return JsonResponse({'status': 'failed', 'message': 'Room not found'}, status=404)

        message_text = data.get('message')
        if not message_text:
            return JsonResponse({'status': 'failed', 'message': 'Message cannot be empty'}, status=400)
        
        room_users = room.user.all()
        
        actual_user = room_users[0] if room_users[0].username != 'bot' else room_users[1]
        
        human_msg = Messeges.objects.create(user=actual_user, room=room, message=message_text)
        human_msg.save()

        bot_reply = f"Hello, How can I help you, {request.user.username}?"
        bot_user = User.objects.get(username='bot')
        reply = Messeges.objects.create(user=bot_user, room=room, message=bot_reply)
        reply.save()
        
        return JsonResponse({'status': 'success',
                             'message': 'Message Sent Successfully',
                             'user_message': MessegesSerializer(human_msg).data,
                             'bot_reply': reply.message}, safe=False)
    return JsonResponse({'status': 'failed', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def logout(request):
    auth_logout(request)  # This clears the session
    return JsonResponse({'status': 'success',
                         'message': 'Logged out successfully'}, safe=False)
