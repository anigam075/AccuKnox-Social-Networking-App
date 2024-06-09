from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone
from .models import FriendRequest
from .serializers import *
from django.core.exceptions import ObjectDoesNotExist

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        Token.objects.create(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email'].lower()
        password = serializer.validated_data['password']
        user = authenticate(username=email, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_search(request):
    serializer = UserSearchSerializer(data=request.data)
    if serializer.is_valid():
        query = serializer.validated_data['query'].lower()
        if not query:
            return Response({'error': 'Query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        all_users = User.objects.all()
        if '@' in query:
            filtered_users = [user for user in all_users if user.email.lower() == query]
        else:
            filtered_users = [user for user in all_users if query in user.first_name.lower() or query in user.last_name.lower()]
        
        serializer = UserSerializer(filtered_users, many=True)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_friend_request(request):
    serializer = SendFriendRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        to_user = User.objects.filter(email=email).first()
        from_user = request.user

        if not to_user:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(from_user=from_user, created_at__gte=timezone.now()-timedelta(minutes=1)).count() >= 3:
            return Response({'error': 'Cannot send more than 3 friend requests within a minute'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def list_friend_requests(request):
#     user = request.user
#     friend_requests = FriendRequest.objects.all()
#     serializer = FriendRequestSerializer(friend_requests, many=True)
#     return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_friend_request(request):
    serializer = RespondFriendRequestSerializer(data=request.data)
    if serializer.is_valid():
        action = serializer.validated_data['action']
        to_user_email = serializer.validated_data['to_user']

        from_user = request.user
        to_user = User.objects.filter(email=to_user_email).first()

        if not to_user:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest.objects.filter(from_user=from_user, to_user=to_user).first()

        if not friend_request:
            return Response({'error': 'Friend request does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'accept':
            friend_request.status = 'accepted'
        elif action == 'reject':
            friend_request.status = 'rejected'
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        friend_request.save()
        return Response(FriendRequestSerializer(friend_request).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_friends(request):
    user = request.user
    friends = User.objects.filter(
        Q(sent_requests__to_user=user, sent_requests__status='accepted') |
        Q(received_requests__from_user=user, received_requests__status='accepted')
    )
    serializer = UserSerializer(friends, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending_requests(request):
    user = request.user
    pending_requests = FriendRequest.objects.filter(to_user=user, status='pending')
    serializer = FriendRequestSerializer(pending_requests, many=True)
    return Response(serializer.data)
