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


class CategoriesView(generics.ListCreateAPIView):
	queryset = models.Category.objects.all()
	serializer_class = serializers.CategorySerializer

	def get_permissions(self):
		permisson_classes = []
		if self.request.method != 'GET':
			permisson_classes = [IsAuthenticated]
		return [permisson() for permisson in permisson_classes]


class MenuItemsView(generics.ListCreateAPIView):
	permission_classes = [IsAuthenticated]
	queryset = models.MenuItem.objects.all()
	serializer_class = serializers.MenuItemSerializer

	ordering_fields = ['price', 'inventory']
	filterset_fields = ['price']
	search_fields = ['category__title']

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

	def get_permissions(self):
		permission_classes = []
		if self.request.method != 'GET':
			permission_classes = [IsAuthenticated]
		return [permission() for permission in permission_classes]


class CartView(generics.ListCreateAPIView):
	permission_classes = [IsAuthenticated]
	queryset = models.Cart.objects.all()
	serializer_class = serializers.CartSerializer

	def get_queryset(self):
		return models.Cart.objects.all().filter(user=self.request.user)

	def delete(self, request):
		cart = models.Cart.objects.filter(user__pk=request.user.pk)
		cart.delete()
		return Response({'message': 'User deleted Cart successfully'}, status=status.HTTP_200_OK)


class OrderView(generics.ListCreateAPIView):
	permission_classes = [IsAuthenticated]
	queryset = models.Order.objects.all()
	serializer_class = serializers.OrderSerializer

	def get_queryset(self):
		if self.request.user.is_superuser:
			return models.Order.objects.all()
		elif self.request.user.groups.count() == 0:
			return models.Order.objects.filter(user=self.request.user)
		elif self.request.user.groups.filter(name='Delivery crew').exists():
			return models.Order.objects.filter(delivery_crew=self.request.user)
		else:  # delivery crew or manager
			return models.Order.objects.all()

	def create(self, request, *args, **kwargs):
		menuitem_count = models.Cart.objects.filter(user=self.request.user).count()
		if menuitem_count == 0:
			return Response({'message': 'No Item in Cart'})
		data = request.data.copy()
		total = self.get_total_price(self.request.user)
		data['total'] = total
		data['user'] = self.request.user.id
		order_serializer = serializers.OrderSerializer(data=data)
		if order_serializer.is_valid():
			order = order_serializer.save()

			items = models.Cart.objects.filter(user=self.request.user).all()

			for item in items.values():
				order_item = models.OrderItem(
					order=order,
					menuitem_id=item['menuitem_id'],
					price=item['price'],
					quantity=item['quantity']
				)
				order_item.save()

			models.Cart.objects.filter(user=self.request.user).delete()

			result = order_serializer.data.copy()
			result['total'] = total
			return Response(order_serializer.data)

	def get_total_price(self, user):
		total = 0
		items = models.Cart.objects.filter(user=user).all()
		for item in items.values():
			total += item['price']
		return total


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
	permission_classes = [IsAuthenticated]
	queryset = models.Order.objects.all()
	serializer_class = serializers.OrderSerializer

	def update(self, request, *args, **kwargs):
		if self.request.user.groups.count() == 0:
			return Response({'message': 'Not ok'})
		else:  # everyone else - Super Admin, Manager and Delivery Crew
			return super().update(request, *args, **kwargs)


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


# class GroupViewSet(viewsets.ViewSet):
# 	permission_classes = [IsAdminUser]
#
# 	def list(self, request):
# 		users = User.objects.all().filter(groups__name='Manager')
# 		items = UserSerilializer(users, many=True)
# 		return Response(items.data)
#
# 	def create(self, request):
# 		user = get_object_or_404(User, username=request.data['username'])
# 		managers = Group.objects.get(name="Manager")
# 		managers.user_set.add(user)
# 		return Response({"message": "user added to the manager group"}, 200)
#
# 	def destroy(self, request):
# 		user = get_object_or_404(User, username=request.data['username'])
# 		managers = Group.objects.get(name="Manager")
# 		managers.user_set.remove(user)
# 		return Response({"message": "user removed from the manager group"}, 200)
#
#
# class DeliveryCrewViewSet(viewsets.ViewSet):
# 	permission_classes = [IsAuthenticated]
#
# 	def list(self, request):
# 		users = User.objects.all().filter(groups__name='Delivery Crew')
# 		items = UserSerilializer(users, many=True)
# 		return Response(items.data)
#
# 	def create(self, request):
# 		# only for super admin and managers
# 		if self.request.user.is_superuser == False:
# 			if self.request.user.groups.filter(name='Manager').exists() == False:
# 				return Response({"message": "forbidden"}, status.HTTP_403_FORBIDDEN)
#
# 		user = get_object_or_404(User, username=request.data['username'])
# 		dc = Group.objects.get(name="Delivery Crew")
# 		dc.user_set.add(user)
# 		return Response({"message": "user added to the delivery crew group"}, 200)
#
# 	def destroy(self, request):
# 		# only for super admin and managers
# 		if self.request.user.is_superuser == False:
# 			if self.request.user.groups.filter(name='Manager').exists() == False:
# 				return Response({"message": "forbidden"}, status.HTTP_403_FORBIDDEN)
# 		user = get_object_or_404(User, username=request.data['username'])
# 		dc = Group.objects.get(name="Delivery Crew")
# 		dc.user_set.remove(user)
# 		return Response({"message": "user removed from the delivery crew group"}, 200)