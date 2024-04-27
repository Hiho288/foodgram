from rest_framework.pagination import PageNumberPagination

from foodgram_backend.settings import PAGE_SIZE


class RecipePaginator(PageNumberPagination):
    page_size = PAGE_SIZE
