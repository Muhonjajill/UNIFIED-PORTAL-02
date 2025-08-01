# core/utils.py
def is_director(user):
    return user.is_superuser or user.groups.filter(name='Director').exists()

def is_manager(user):
    return user.groups.filter(name='Manager').exists()

def is_staff(user):
    return user.groups.filter(name='Staff').exists()

def can_user_access_file(self, user):
    if self.access_level == 'public':
        return True
    if self.access_level == 'restricted':
        return user.has_perm('core.view_file')
    if self.access_level == 'confidential':
        return self.uploaded_by == user or user.is_superuser
    return False
