from rest_framework.pagination import PageNumberPagination

from foodgram_backend.settings import PAGE_SIZE


class RecipePaginator(PageNumberPagination):
    page_size = PAGE_SIZE


class RecipePaginator(PageNumberPagination):
    page_size = PAGE_SIZE

    def get_page_size(self, request):
        page_size = request.query_params.get('limit')
        if page_size and page_size.isdigit():
            return int(page_size)
        return self.page_size
