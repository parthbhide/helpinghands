from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    is_donor = models.BooleanField('donor status', default=False)
    is_receiver = models.BooleanField('receiver status', default=False)
    is_volunteer = models.BooleanField('volunteer status', default=False)
    address = models.TextField(max_length = 200, default = "")
    registration_number = models.BigIntegerField(null = True,unique = True)
    contact_number = models.BigIntegerField(null = True)
    ngo_name = models.CharField(null = True,max_length=50)
    class Meta:
        db_table = 'User'
    
'''class donor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, default = "")
    address = models.TextField(max_length = 200, default = "")
    class Meta:
        db_table = 'donor'
        
class receiver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, default = "")
    address = models.TextField(max_length = 200, default = "")
    class Meta:
        db_table = 'receiver'

class volunteer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, default = "")
    address = models.TextField(max_length = 200, default = "")
    class Meta:
        db_table = 'volunteer'
'''

class stock(models.Model):
    category = models.CharField(max_length = 20, primary_key = True)
    quantity = models.IntegerField()
    class Meta:
        db_table = 'stock'
        
class donation_drive(models.Model):
    date = models.DateField(primary_key = True)
    class Meta:
        db_table = 'donation_drive'

class collection_drive(models.Model):
    date = models.DateField(primary_key = True)
    class Meta:
        db_table = 'collection_drive'
        
class collected_by(models.Model):
    volunteer = models.ForeignKey(User, on_delete = models.CASCADE)
    date = models.ForeignKey(collection_drive, on_delete = models.CASCADE)
    class Meta:
        db_table = 'collected_by'
        
class donated_by(models.Model):
    volunteer = models.ForeignKey(User, on_delete = models.CASCADE)
    date = models.ForeignKey(donation_drive, on_delete = models.CASCADE)
    class Meta:
        db_table = 'donated_by'
        
class donates_items_in(models.Model):
    donor = models.ForeignKey(User, on_delete = models.CASCADE)
    date = models.ForeignKey(collection_drive, on_delete = models.CASCADE)
    category = models.ForeignKey(stock, on_delete = models.CASCADE)
    quantity = models.IntegerField()
    description = models.CharField(max_length = 50, null = True)
    class Meta:
        unique_together = (('donor','date','category'),)
        db_table = 'donates_items_in'
        
class receives_items_in(models.Model):
    receiver = models.ForeignKey(User, on_delete = models.CASCADE)
    date = models.ForeignKey(donation_drive, on_delete = models.CASCADE)
    category = models.ForeignKey(stock, on_delete = models.CASCADE)
    quantity = models.IntegerField()
    class Meta:
        unique_together = (('receiver','date','category'),)
        db_table = 'receives_items_in'

class reports(models.Model):
    donation_drive_date = models.ForeignKey(donation_drive, null=True, on_delete=models.CASCADE)
    collection_drive_date = models.ForeignKey(collection_drive, null=True, on_delete=models.CASCADE)
    filepath= models.FileField(upload_to='files/', null=True, verbose_name="")
    class Meta:
        db_table = 'reports'
