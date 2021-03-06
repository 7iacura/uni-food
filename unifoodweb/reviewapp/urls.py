from django.urls import path
from . import views

urlpatterns = [

	# /reviewapp/
	path('', views.index, name='index'),

	# /dataset/
	path('dataset/', views.dataset, name='dataset'),
	# /dataset-remove/
	path('dataset-remove/', views.dataset_remove, name='dataset_remove'),

	# /users/
	path('users/', views.users, name='users'),
	# /user/X/
	path('user/<str:user_id>', views.user, name='user'),
	# /user_experience/
	path('user-experience/<str:user_id>', views.user_experience, name='user-experience'),

	# /products/
	path('products/', views.products, name='products'),
	# /product/X/
	path('product/<str:product_id>', views.product, name='product'),

	# /ratings/
	path('ratings/', views.ratings, name='ratings'),
	# /rating/X/
	path('rating/<int:rating_id>', views.rating, name='rating'),

	# /topics/
	path('topics/', views.topics, name='topics'),
	# /topic/X/
	path('topic/<int:topic_id>', views.topic, name='topic'),

	# /dashboard/
	path('dashboard/', views.dashboard, name='dashboard'),

]
