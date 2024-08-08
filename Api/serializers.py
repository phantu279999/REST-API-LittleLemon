from rest_framework import serializers
from . import models


class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Category
		fields = [
			'id',
			'title',
			'slug'
		]


class MenuItemSerializer(serializers.ModelSerializer):
	category_id = serializers.IntegerField(write_only=True)
	category = CategorySerializer(read_only=True)

	class Meta:
		model = models.MenuItem
		fields = [
			'title',
			'price',
			'featured',
			'category',
			'category_id',
		]


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.User
		fields = ['id', 'username', 'email']


class CartSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Cart
		fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.OrderItem
		fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
	orderitem = OrderItemSerializer(many=True, read_only=True, source='order')

	class Meta:
		model = models.Order
		fields = [
			'id', 'user', 'delivery_crew', 'status', 'date', 'total', 'orderitem'
		]
