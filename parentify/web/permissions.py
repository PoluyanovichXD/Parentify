from django.http import Http404

class UserPermisions(object):
    ACCESS_ONLY_ADMIN = [
        '/admin'
    ]
    NO_ACCESS_USER_LINKS = {
        'user': [],
        'not_user': []
    }

    def __init__(self, user=None):
        self.user = user

    def check_user_permisions(self, request):
        for item in self.no_access_links:
            if request.path.startswith(item):
                return False
        return True

    @property
    def type_user(self):
        if self.user:
            if self.user.is_admin:
                return 'admin'
            else:
                return 'user'
        return 'not_user'
    
    @property
    def no_access_links(self):
        if self.type_user!='admin':
            links = self.NO_ACCESS_USER_LINKS[self.type_user]
            links = links + ACCESS_ONLY_ADMIN
            return links
        return []