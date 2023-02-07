from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ApiSignup, CategoryViewSet, CommentViewSet, GenreViewSet,
                    GetApiToken, ReviewViewSet, TitleViewSet, UsersViewSet)

router_v1 = DefaultRouter()
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)
router_v1.register(
    r'titles/(?P<title>\d+)/reviews',
    ReviewViewSet, basename='review')
router_v1.register('users', UsersViewSet, basename='user')
router_v1.register('titles', TitleViewSet, basename='title')
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genre')


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/token/', GetApiToken.as_view(), name='get_token'),
    path('v1/auth/signup/', ApiSignup.as_view(), name='signup')
]
