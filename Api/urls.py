from django.urls import path, include
from . import views


urlpatterns = [
	path('categories/', views.CategoriesView.as_view()),
	path('menu-items/', views.MenuItemsView.as_view()),
	path('cart/menu-items/', views.CartView.as_view()),
	path('orders/', views.OrderView.as_view()),
	path('orders/<int:pk>', views.OrderDetailView.as_view()),

	path('groups/<str:group_name>/users/', views.UserInGroupView.as_view()),
	path('groups/<str:group_name>/users/<int:user_pk>/', views.UserInGroupView.as_view()),

]