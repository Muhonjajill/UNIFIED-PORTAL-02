from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class EmailOTP(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE)
        otp = models.CharField(max_length=6)
        created_at = models.DateTimeField(auto_now_add=True)

        def is_expired(self):
            now = timezone.now()
            return now >  self.created_at + timedelta(minutes=50) 
        
        def __str__(self):
            return f"{self.user.username} - {self.otp}"
        
# File Management Models
class FileCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=255, default='default_icon')

    def __str__(self):
        return self.name
    
ACCESS_LEVEL_CHOICES = [
    ('confidential', 'Confidential'),
    ('restricted', 'Restricted'),
    ('public', 'Public'),
]

class File(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='uploads/files/')
    category = models.ForeignKey(FileCategory, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    authorized_users = models.ManyToManyField(User, blank=True, related_name='authorized_files')
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVEL_CHOICES, default='restricted')

    def can_user_access(self, user):
        if self.access_level == 'public':
            return True
        if self.access_level == 'restricted':
            return user in self.authorized_users.all() or user.has_perm('core.view_file')
        if self.access_level == 'confidential':
            return self.uploaded_by == user or user.is_superuser
        return False
    
    def __str__(self):
        return self.title

class FileAccessLog(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    accessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    access_time = models.DateTimeField(auto_now_add=True)

def user_directory_path(instance, filename):
    return f'user_{instance.user.id}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=user_directory_path, blank=True, null=True)

    def __str__(self):
        return self.user.username


# Help desk models
class Unit(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Terminal(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    branch_name = models.CharField(max_length=100, default='Main Branch')
    cdm_name = models.CharField(max_length=100, default='CDM-Default')
    serial_number = models.CharField(max_length=100, unique=True, default='SN0000')
    region = models.ForeignKey('Region', on_delete=models.CASCADE, null=True)
    model = models.CharField(max_length=100, default='ModelX')
    zone = models.ForeignKey('Zone', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.customer.name if self.customer else 'No Customer'} - {self.branch_name}"


class SystemUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    role = models.CharField(max_length=50)

    def __str__(self):
        return self.username

class Zone(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ProblemCategory(models.Model):
    brts_unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.brts_unit.name})"
    
class VersionControl(models.Model):
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE)
    manufacturer = models.CharField(max_length=100)
    template = models.CharField(max_length=100)
    firmware = models.CharField(max_length=100)
    xfs = models.CharField(max_length=100,  default='N/A')  
    ejournal = models.CharField(max_length=100,  default='N/A') 
    responsible = models.CharField(max_length=100,  default='N/A')  
    app_version = models.CharField(max_length=100,  default='1.0.0') 
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.terminal} - {self.firmware}"
class VersionComment(models.Model):
    version = models.ForeignKey(VersionControl, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]  #  
class Report(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50)
    generated_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='reports/')

    def __str__(self):
        return self.name

    def download_url(self):
        return self.file.url


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    ISSUE_TYPES = [
    ('technical outage', 'Technical Outage'),
    ('cybersecurity incident', 'Cybersecurity Incident'),
    ('client complaint', 'Client Complaint'),
    ('sla breach', 'SLA Breach'),
    ]

    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    title = models.CharField(max_length=255, null=True)
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPES, default='technical outage')
    brts_unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)
    problem_category = models.ForeignKey(ProblemCategory, on_delete=models.SET_NULL, null=True)
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False, blank=False)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=False, blank=False)

    created_by = models.ForeignKey(User, related_name='created_tickets', on_delete=models.SET_NULL, null=True)
    assigned_to = models.ForeignKey(User, related_name='assigned_tickets', on_delete=models.SET_NULL, null=True, blank=True)
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    resolution = models.TextField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, related_name='resolved_tickets', null=True, blank=True, on_delete=models.SET_NULL)
    resolved_at = models.DateTimeField(null=True, blank=True)
    comment_summary = models.TextField(blank=True, null=True)

    is_escalated = models.BooleanField(default=False)
    escalated_at = models.DateTimeField(null=True, blank=True)
    escalated_by = models.ForeignKey(
        User, null=True, blank=True, related_name='escalated_tickets', on_delete=models.SET_NULL
    )
    escalation_reason = models.TextField(null=True, blank=True)

    # Optional: to escalate to another user
    # escalated_to = models.ForeignKey(User, null=True, blank=True, related_name='tickets_escalated_to', on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        permissions = [
            ('can_view_ticket', 'Can view ticket'),
            ('can_resolve_ticket', 'Can resolve ticket'),
        ]

    def __str__(self):
        return self.title

class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticket.id}" - {self.created_by} 