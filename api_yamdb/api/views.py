from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

from api_yamdb.settings import OUR_EMAIL

from .filters import TitleFilter
from .permissions import IsAdmin, IsAdminOrReadOnly, ReviewPermissions
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          TokenSerializer, UserSerializer, SignUpSerializer)


class TitleViewSet(viewsets.ModelViewSet):
    """View-класс реализующий операции модели Title."""

    queryset = Title.objects.all().annotate(rating=Avg('review__score'))
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    search_fields = ('name',)
    filterset_class = TitleFilter

    def get_serializer_class(self):

        if self.action in ('list', 'retrieve'):

            return TitleReadSerializer

        return TitleWriteSerializer


class CreateListDeleteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Mixins классов Genre и Category."""

    pass


class GenreViewSet(CreateListDeleteViewSet):
    """View-класс реализующий операции модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'slug'
    search_fields = ('name',)


class CategoryViewSet(CreateListDeleteViewSet):
    """View-класс реализующий операции модели Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'slug'
    search_fields = ('name',)


class ReviewViewSet(viewsets.ModelViewSet):
    """View-класс реализующий операции модели Review."""

    serializer_class = ReviewSerializer
    permission_classes = [ReviewPermissions, ]

    def get_queryset(self):

        get_title = get_object_or_404(
            Title, pk=self.kwargs.get('title')
        )

        return Review.objects.filter(title=get_title)

    def perform_create(self, serializer):

        get_title = get_object_or_404(
            Title, pk=self.kwargs.get('title')
        )
        serializer.save(author=self.request.user, title=get_title)


class CommentViewSet(viewsets.ModelViewSet):
    """View-класс реализующий операции модели Comment."""

    serializer_class = CommentSerializer
    permission_classes = [ReviewPermissions, ]

    def get_queryset(self):

        return Comment.objects.filter(review_id=self.kwargs.get('review_id'))

    def perform_create(self, serializer):

        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        get_review = get_object_or_404(
            Review, pk=review_id, title_id=title_id
        )
        serializer.save(author=self.request.user, review=get_review)


class UsersViewSet(viewsets.ModelViewSet):
    """View-класс реализующий операции модели Users."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', )

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):

        if request.method == 'GET':
            serializer = UserSerializer(request.user)

            return Response(serializer.data)
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)

        return Response(serializer.data)


class GetApiToken(APIView):
    """Получение JWT-токена и кода подтверждения"""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):

        serializer = TokenSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'confirmation_code': 'Неверный код подтверждения!'},
                status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:

            return Response(
                {'username': 'Пользователь не найден!'},
                status=status.HTTP_404_NOT_FOUND)

        if data.get('confirmation_code') == user.confirmation_code:
            token = RefreshToken.for_user(user).access_token

            return Response({'token': str(token)},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApiSignup(APIView):
    """Регистрация и получение кода подтверждения на email."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):

        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = get_object_or_404(
            User, username=serializer.validated_data['username']
        )

        confirmation_code = default_token_generator.make_token(user)
        user.confirmation_code = confirmation_code
        user.save()

        send_mail(
            subject='Код подтверждения',
            message=(
                'Код подтверждения'
                f'для доступа регистрации: {confirmation_code}'
            ),
            from_email=OUR_EMAIL,
            recipient_list=[user.email],
        )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
