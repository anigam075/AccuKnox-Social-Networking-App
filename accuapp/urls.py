from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('search/', user_search, name='user-search'),
    path('friend-request/', send_friend_request, name='send-friend-request'),
    path('friend-request/respond/', respond_friend_request, name='respond-friend-request'),
    path('friends/', list_friends, name='list-friends'),
    path('pending-requests/', list_pending_requests, name='list-pending-requests'),
    # path('friend-requests/', list_friend_requests, name='list-friend-requests'), #for test purpose to list all the friends request universally
]