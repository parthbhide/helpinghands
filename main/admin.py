from django.contrib import admin
#from .models import donor
#from .models import receiver
#from .models import volunteer
from .models import stock
from .models import donation_drive
from .models import collection_drive
from .models import collected_by
from .models import donated_by
from .models import donates_items_in
from .models import receives_items_in
from .models import User
<<<<<<< HEAD
from .models import file
from .models import dstock
||||||| 3c3bf57
=======
from .models import reports
>>>>>>> upstream/master

# Register your models here.
admin.site.register(User)
#admin.site.register(donor)
#admin.site.register(receiver)
#admin.site.register(volunteer)
admin.site.register(stock)
admin.site.register(donation_drive)
admin.site.register(collection_drive)
admin.site.register(collected_by)
admin.site.register(donated_by)
admin.site.register(donates_items_in)
<<<<<<< HEAD
admin.site.register(receives_items_in)
admin.site.register(file)
admin.site.register(dstock)
||||||| 3c3bf57
admin.site.register(receives_items_in)
=======
admin.site.register(receives_items_in)
admin.site.register(reports)
>>>>>>> upstream/master
