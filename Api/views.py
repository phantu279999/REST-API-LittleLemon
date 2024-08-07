from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import serializers
from . import models


# check permission of user
class IsManager(IsAuthenticated):
	def has_permission(self, request, view):
		return request.user.is_authenticated and request.user.groups.filter(name='Manager').exists()


class IsCustomerOrDeliveryCrew(IsAuthenticated):
	def has_permission(self, request, view):
		# return request.user.is_authenticated and request.user.groups.filter(name='Delivery crew').exists()
		return request.user.is_authenticated and request.user.groups.filter(name='Delivery crew').exists()


class MenuItemsView(generics.ListCreateAPIView):
	permission_classes = [IsAuthenticated]
	queryset = models.MenuItem.objects.all()
	serializer_class = serializers.MenuItemSerializer

	ordering_fields = ['price']
	filterset_fields = ['price']
	search_fields = ['title']

	def get_permissions(self):
		if self.request.method == 'GET':
			return []
		return [IsAuthenticated()]

	def get_queryset(self):
		queryset = models.MenuItem.objects.all()
		title = self.request.query_params.get('title')
		if title is not None:
			queryset = queryset.filter(menuitem_title=title)
		return queryset


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = models.MenuItem.objects.all()
	serializer_class = serializers.MenuItemSerializer


class UserInGroupView(APIView):
	permission_classes = [IsManager]

	def get(self, request, group_name):
		try:
			if "-" in group_name:
				group_name = group_name.replace("-", " ")
			group = models.Group.objects.get(name=group_name.capitalize())
		except models.Group.DoesNotExist:
			return Response({'error': 'Group does not exist'}, status=status.HTTP_404_NOT_FOUND)

		users = group.user_set.all()
		serializer = serializers.UserSerializer(users, many=True)
		return Response(serializer.data)

	def delete(self, request, group_name, user_pk):
		try:
			if "-" in group_name:
				group_name = group_name.replace("-", " ")
			group = models.Group.objects.get(name=group_name.capitalize())
		except models.Group.DoesNotExist:
			return Response({'error': 'Group does not exist'}, status=status.HTTP_404_NOT_FOUND)

		try:
			user_to_delete = models.User.objects.get(pk=user_pk)
		except models.User.DoesNotExist:
			return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

		if user_to_delete not in group.user_set.all():
			return Response({'error': 'User is not in the specified group'}, status=status.HTTP_400_BAD_REQUEST)

		if user_to_delete == request.user:
			return Response({'error': 'You can\'t delete yourself'}, status=status.HTTP_403_FORBIDDEN)

		group.user_set.remove(user_to_delete)
		return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)


class CartView(generics.ListCreateAPIView):
	permission_classes = [IsAuthenticated]
	queryset = models.Cart.objects.all()
	serializer_class = serializers.CartSerializer

	def delete(self, request):
		cart = models.Cart.objects.filter(user__pk=request.user.pk)
		cart.delete()
		return Response({'message': 'User deleted Cart successfully'}, status=status.HTTP_200_OK)


class OrderView(generics.ListCreateAPIView):
	permission_classes = [IsAuthenticated]
	queryset = models.Order.objects.all()
	serializer_class = serializers.OrderSerializer


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
	permission_classes = [IsAuthenticated]
	queryset = models.Order.objects.all()
	serializer_class = serializers.OrderSerializer
