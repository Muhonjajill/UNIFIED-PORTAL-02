from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import EscalationHistory, File, Profile
from django.core.exceptions import ObjectDoesNotExist

from core.views import escalate_ticket, notify_group


@receiver(post_migrate)
def setup_groups_and_permissions(sender, **kwargs):
    """
    Signal that sets up user groups and file model permissions after migrations.
    """
    # File model permissions
    file_content_type = ContentType.objects.get_for_model(File)

    try:
        # File permissions for CRUD operations on files
        view_file = Permission.objects.get(codename='view_file')
        change_file = Permission.objects.get(codename='change_file')
        delete_file = Permission.objects.get(codename='delete_file')
        add_file = Permission.objects.get(codename='add_file')

        can_edit_file_perm, _ = Permission.objects.get_or_create(
            codename='can_edit_file',
            name='Can edit file',
            content_type=file_content_type
        )

        # User model permissions
        view_user = Permission.objects.get(codename='view_user')
        change_user = Permission.objects.get(codename='change_user')
        delete_user = Permission.objects.get(codename='delete_user')

    except ObjectDoesNotExist:
        return

    # Create groups
    director_group, _ = Group.objects.get_or_create(name='Director')
    manager_group, _ = Group.objects.get_or_create(name='Manager')
    staff_group, _ = Group.objects.get_or_create(name='Staff')

    # Assign permissions to groups
    director_group.permissions.set([
        view_file, change_file, delete_file, add_file, can_edit_file_perm,
        view_user, change_user, delete_user
    ])

    manager_group.permissions.set([
        view_file, change_file, add_file,
        view_user, change_user
    ])

    staff_group.permissions.set([
        view_file, add_file,
        view_user
    ])


@receiver(post_save, sender=User)
def assign_permissions_based_on_group(sender, instance, created, **kwargs):
    """
    Signal handler that assigns permissions dynamically based on the user's group.
    """
    if created:
        # Create user profile if it does not exist
        Profile.objects.create(user=instance)
        
        # Assign group and permissions based on user role
        if instance.is_superuser:
            # Superuser automatically gets all permissions
            admin_group, _ = Group.objects.get_or_create(name='Admin')
            instance.groups.add(admin_group)
            # Assign all available permissions
            assign_all_permissions(instance)
        else:
            # Assign specific group based on role or user type
            if instance.groups.filter(name='Director').exists():
                assign_director_permissions(instance)
            elif instance.groups.filter(name='Manager').exists():
                assign_manager_permissions(instance)
            elif instance.groups.filter(name='Staff').exists():
                assign_staff_permissions(instance)
    else:
        # If the user is updated, you might want to reassign permissions in case their group changed
        if hasattr(instance, 'profile'):
            instance.profile.save()

def assign_all_permissions(user):
    """Assigns all permissions to the user (for superusers or Admin)"""
    permissions = Permission.objects.all()
    user.user_permissions.set(permissions)

def assign_director_permissions(user):
    """Assigns director-specific permissions to the user"""
    # Permissions related to file management and user management
    permissions = [
        'core.view_file',
        'core.change_file',
        'core.delete_file',
        'core.add_file',
        'core.view_user',
        'core.change_user',
        'core.delete_user',
    ]
    assign_permissions(user, permissions)

def assign_manager_permissions(user):
    """Assigns manager-specific permissions to the user"""
    # Permissions related to file management and user management
    permissions = [
        'core.view_file',
        'core.change_file',
        'core.add_file',
        'core.view_user',
        'core.change_user',
    ]
    assign_permissions(user, permissions)

def assign_staff_permissions(user):
    """Assigns staff-specific permissions to the user"""
    # Permissions related to file access and viewing user profiles
    permissions = [
        'core.view_file',
        'core.add_file',
        'core.view_user',
    ]
    assign_permissions(user, permissions)

def assign_permissions(user, permissions_list):
    """Helper function to assign a list of permissions to a user"""
    for permission_codename in permissions_list:
        permission = Permission.objects.get(codename=permission_codename)
        user.user_permissions.add(permission)



@receiver(post_save, sender=EscalationHistory)
def send_escalation_notification(sender, instance, **kwargs):
    #handle_escalation(instance)
    # Get the next group of users to be notified based on the escalation level
    # (use your existing 'notify_group' function or implement it here)
    notify_group(instance.to_level, instance.ticket)

    # Fetch email addresses dynamically from settings
    recipient_list = settings.ESCALATION_LEVEL_EMAILS.get(instance.to_level, [])

    if recipient_list:
        send_mail(
            subject=f"Ticket #{instance.ticket.id} has been escalated to {instance.to_level}",
            message=f"""
            Ticket ID: {instance.ticket.id}
            Title: {instance.ticket.title}
            Escalated By: {instance.escalated_by}
            Escalation Level: {instance.to_level}
            Reason: {instance.note}

            View Ticket: http://127.0.0.1:8000/tickets/{instance.ticket.id}

            """,
            from_email="godblessodhiambo@gmail.com",
            recipient_list=settings.ESCALATION_LEVEL_EMAILS.get(instance.to_level, []),
            fail_silently=False,
        )
    else:
        # Handle case when no email group is found for the escalation level
        print(f"No email group found for escalation level {instance.to_level}")

