from rest_framework.pagination import CursorPagination


class CommentCursorPagination(CursorPagination):
    ordering = '-dtCreated'
    page_size = 15


class SubCommentCursorPagination(CursorPagination):
    ordering = 'dtCreated'
    page_size = 15


class PaginationHandlerMixin(object):
    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        else:
            pass
        return self._paginator

    def paginate_queryset(self, queryset):

        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset,
                                                self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


class WebtoonCursorPagination(CursorPagination):
    page_size = 9
    ordering = '-id'


class EpisodeImageCursorPagination(CursorPagination):
    page_size = 10
    ordering = 'id'

class EpisodeCursorPagination(CursorPagination):
    page_size = 15
    ordering = ['-episodeNumber']
