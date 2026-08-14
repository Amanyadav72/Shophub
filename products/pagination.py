from rest_framework.pagination import PageNumberPagination

class ShopHubPagination(PageNumberPagination):
    # Default number of items per page if the frontend doesn't specify
    page_size = 4
    
    # Allows the React frontend to ask for a specific chunk size (e.g., ?page_size=20)
    page_size_query_param = 'page_size' 
    
    # Hard limit to protect the database from memory crashes
    max_page_size = 50