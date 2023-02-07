from django.forms import ValidationError
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    """Преобразование данных класса User"""

    class Meta:
        model = User
        lookup_field = 'username'
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class SignUpSerializer(serializers.ModelSerializer):
    """Преобразование Sign Up."""

    def validate(self, attrs):
        if attrs['username'] == 'me':
            raise ValidationError(
                'Пожалуйста, выберите другой ник. Этот нам не нравится :('
            )

        return attrs

    class Meta:
        model = User
        lookup_field = 'username'
        fields = (
            'username',
            'email'
        )


class RoleSerializer(serializers.ModelSerializer):
    """Преобразование данных класса Role"""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')
        read_only_fields = ('role',)


class TokenSerializer(serializers.ModelSerializer):
    """Преобразование данных Tokena."""

    username = serializers.CharField(max_length=150, required=True,)
    confirmation_code = serializers.CharField(required=True,)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class CategorySerializer(serializers.ModelSerializer):
    """Преобразование данных Category."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Преобразование данных Genre."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Преобразование данных Title при чтении."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'genre',
            'category',
            'description',
            'rating'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    """Преобразование данных Title при создании."""

    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'genre',
            'category',
            'description',
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Преобразование данных Review"""

    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True, )
    title = serializers.SlugRelatedField(slug_field='name', read_only=True, )

    def validate(self, data):
        """Отслеживание и запрет повторных отзывов"""

        super().validate(data)

        if self.context['request'].method != 'POST':

            return data

        user = self.context['request'].user
        title_id = (self.context['request'].parser_context['kwargs']['title'])

        if Review.objects.filter(author=user, title__id=title_id).exists():

            raise serializers.ValidationError(
                "Вы уже оставили отзыв на данное произведение")

        return data

    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    """Преобразование данных Comment."""

    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'review', 'author', 'pub_date', 'text')
