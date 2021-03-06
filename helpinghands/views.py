from django.shortcuts import render,redirect
#from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from main.models import collection_drive
from main.models import donation_drive
from main.models import donates_items_in
from main.models import stock
from datetime import date,datetime
from main.models import receives_items_in
from main.models import collected_by
from main.models import donated_by
from main.models import reports
import pandas as pd
import numpy as np
from jinja2 import Environment, FileSystemLoader
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO
from io import StringIO
from django.http import HttpResponse
from django.template.loader import get_template
from helpinghands.settings import MEDIA_ROOT
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from main.token import account_activation_token
from django.contrib.sites.shortcuts import get_current_site




User = get_user_model()


def contact(request):
    if request.method == 'POST':
        if request.POST["message"] and request.POST["name"] and request.POST["email"] and request.POST["subject"]:
            content = request.POST["message"]
            name = request.POST["name"]
            email = request.POST["email"]
            subject = request.POST["subject"]

            email = EmailMessage(
                subject,
                content,
                "admin@helpinghands.in",
                ['parthbhide391@gmail.com'],
                headers = {'Reply-To': email }
            )

            email.send()

            return render(request, 'index.html', {'message' : 'Message Sent !!'})

        else:
            return render(request, 'index.html', {'error' : 'All fields are required !!'})
    return render(request,'contact.html')

def home(request):
    return render(request, 'index.html')

def aboutus(request):
    return render(request, 'aboutus.html')

def demo(request):
    return render(request, 'admin.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(username=uid)
        print(type(uid))
        print(account_activation_token.check_token(user, token))
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        auth.login(request, user)
        # return redirect('home')
        return render(request, 'index.html', {'message' : 'Email verified !!'})
    else:
        return render(request, 'index.html', {'message' : 'Email verification link is invalid !!'})
    
    
def user_signup(request):
    if request.method == 'POST':
        if request.POST['password'] == request.POST['cnf-password']:
            try:
                user = User.objects.get(username = request.POST['username'])
                return render(request, 'user-registration.html' , {'error' : 'Username already taken !!'})
            except User.DoesNotExist:
                donor_check = False
                volunteer_check = False
                if request.POST['user_type'] == 'is_donor':
                    donor_check = True
                else:
                    volunteer_check = True
                user = User.objects.create_user(request.POST['username'],password = request.POST['password'],
                                                first_name = request.POST['firstname'], last_name=request.POST['lastname'], 
                                                address =  request.POST['address'], email = request.POST['email'],
                                                contact_number = request.POST['mobile'],is_donor= donor_check, is_volunteer = volunteer_check, is_active = False)
                        
                #env = Environment(loader=FileSystemLoader('./templates'))
                #template = env.get_template("acc_activate_email.html")
                current_site = get_current_site(request)
                email_subject = 'Activate Your Account'
              #  message = 'Please click the following link to activate your account' 
                #to_email = form.cleaned_data.get('email')
                message = render_to_string('acc_activate_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.username)),
                'token':account_activation_token.make_token(user),
            })
           # to_email = form.cleaned_data.get('email')
                email = EmailMessage(email_subject, message, to=[request.POST['email']])
                email.send()
                return render(request, 'index.html', {'message' : 'Please verify your email address to login to your account !!'})
        else:
            return render(request, 'user-registration.html' , {'error' : 'Passwords must match !!'})
        #user wants to signup
    else:
        #user is requesting singup page
        if request.session.has_key('username'):
            return render(request, 'index.html', {'message' : 'You are already logged in !!'})
        return render(request, 'user-registration.html')
    
def ngo_signup(request):
    if request.method == 'POST':
        if request.POST['password'] == request.POST['cnf-password']:
            try:
                user = User.objects.get(username = request.POST['username'])
                return render(request, 'ngo-registration.html' , {'error' : 'Username already taken !!'})
            except User.DoesNotExist:
                donor_check = False
                volunteer_check = False
                ngo_check = True
                try:
                    user = User.objects.create_user(request.POST['username'],password = request.POST['password'],
                                                    ngo_name = request.POST['ngo-name'], registration_number = request.POST['reg_number'],
                                                    address =  request.POST['address'], email = request.POST['email'],
                                                    contact_number = request.POST['mobile'],is_donor= donor_check, is_volunteer = volunteer_check, is_receiver = ngo_check, is_active = False)
                    #auth.login(request, user)
                    #return redirect('home')
                    current_site = get_current_site(request)
                    email_subject = 'Activate Your Account'
                    message = render_to_string('acc_activate_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid':urlsafe_base64_encode(force_bytes(user.username)),
                    'token':account_activation_token.make_token(user),
                    })
                    email = EmailMessage(email_subject, message, to=[request.POST['email']])
                    email.send()
                    return render(request, 'index.html', {'message' : 'Please verify your email address to login to your account !!'})
                    
                except IntegrityError:
                    return render(request, 'ngo-registration.html' , {'error' : 'NGO with this Registration Number already registered with us !!'})
        else:
            return render(request, 'ngo-registration.html' , {'error' : 'Passwords must match !!'})
        #user wants to signup
    else:
        #user is requesting singup page
        if request.session.has_key('username'):
            return render(request, 'index.html', {'message' : 'You are already logged in !!'})
        return render(request, 'ngo-registration.html')
    

def login(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['username'],password=request.POST['password'])
        if user is not None:
            auth.login(request, user)
            if user.is_donor:
                request.session['username'] = user.username
                return redirect('donorhome')
            if user.is_receiver:
                request.session['username'] = user.username
                return redirect('receiverhome')
            if user.is_staff:
                request.session['username'] = user.username
                return redirect('adminhome')
        else:
            try:
                u = User.objects.get(username=request.POST['username'])
                if u and not u.is_active :
                    return render(request, 'login.html',{'error' : 'Email address not verified !!\nVerify your email address to login to your account !!'})    
            except:
                pass
            return render(request, 'login.html',{'error' : 'Worng credentials !!'})    
    else:
        if request.session.has_key('username'):
            return render(request, 'index.html', {'message' : 'You are already logged in !!'})
        return render(request, 'login.html')


def logout(request):
    if request.method == 'POST':
        try:
          del request.session['username']
        except:
          pass
        auth.logout(request)
        return redirect('home')
    
    return render(request, 'login.html')
        
@login_required(login_url='/login/')
def donorhome(request):
    dates = collection_drive.objects.all()
    _details = donates_items_in.objects.all()
    flag = False
    e = ''
    #checks if current user has already registered for any upcomming donation drive (at time of login)
    for _ in _details:
        if _.donor == request.user and _.date.date > date.today():
            flag = True
            e = '\n You are already registerd for upcomming doantion drive on date '+ (_.date.date).strftime('%d-%m-%Y') + "\n" +' You cannot register in more than one donation drive at a time.'
    c = {}
    i = 0
    #gets dates of next three donation drives
    for d in dates:
        if not(i < 3):
            break
        if d.date > date.today():
            c[i] = d
            i += 1
    if request.method == 'POST':
        #if user tries to register for donation drive multiple times ( after login )
        for _ in _details:
                if _.donor == request.user and _.date.date > date.today():
                    flag = True
                    e = 'You are already registerd for upcomming doantion drive on date '+ (_.date.date).strftime('%d-%m-%Y') + "\n" +' You cannot register in more than one donation drive at a time.'
        if flag :
            return render(request, 'donorloginscreen.html' ,{'dates': c , 'len': range(len(c)), 'flag':flag, 'e':e })
        else: 
            #POST.get is used because date has to be choosen form multiple values and it will return False if nothing is selected
            if request.POST['cloths-qty'] and request.POST['footwear-qty'] and request.POST['stationary-qty'] and request.POST.get('date',False):
                s = stock.objects.all()
                for x in s:
                    category_qty = str(x.category).lower()+"-qty"
                    category_disc = str(x.category).lower()+"-disc"
                    donation_detail = donates_items_in()
                    donation_detail.category = x
                    donation_detail.quantity = int(request.POST[category_qty])
                    donation_detail.description = request.POST[category_disc]
                    #gets id number returned from the user and gets the corresponding collection drive object form the list c
                    donation_detail.date = c[int(request.POST['date'])]
                    donation_detail.donor = request.user
                    if int(request.POST[category_qty]) > 0:
                        donation_detail.save()
                return render(request, 'donorloginscreen.html' ,{'error' : 'Your Donation details are saved !! ', 'dates': c , 'len': range(len(c)), 'flag':flag, 'e':e })
            else:
                #if all required details are not filled by user
                return render(request, 'donorloginscreen.html' ,{'error' : 'All details are required !! ','dates': c , 'len': range(len(c)), 'flag':flag, 'e':e })
    #if it is a GET request means user has logged in so return the donation home screen
    else:
        if request.user.is_receiver or request.user.is_volunteer:
            return render(request, 'index.html', {'message' : 'You are not authorized to go to donors page !!'})

        return render(request, 'donorloginscreen.html', {'dates': c , 'len': range(len(c)), 'flag': flag, 'e':e })
    
@login_required(login_url='/login/')
def receiverhome(request):
    dates = donation_drive.objects.all()
    curr_stock = stock.objects.all()
    cloths = 0
    stationary = 0
    footwear = 0
    c = {}
    i = 0
    flag = False
    e = ''
    #gets dates of next three donation drives
    for d in dates:
        if not(i < 3):
            break
        if d.date > date.today():
            c[i] = d
            i += 1
    #gets quantity and category of all objects of stock
    for cs in curr_stock:
        if cs.category == 'cloths':
            cloths = cs.quantity
        if cs.category == 'stationary':
            stationary = cs.quantity
        if cs.category == 'footwear':
            footwear = cs.quantity
            
    if request.method == 'POST':
        if request.POST['req-cloths-qty'] and request.POST['req-footwear-qty'] and request.POST['req-stationary-qty'] and request.POST.get('date',False):
            s = stock.objects.all()
            for x in s:
                category_qty = "req-"+str(x.category).lower()+"-qty"
                category_disc = "req-"+str(x.category).lower()+"-disc"
                req_detail = receives_items_in()
                req_detail.category = x
                req_detail.date = c[int(request.POST['date'])]
                req_detail.quantity = int(request.POST[category_qty])
                req_detail.receiver = request.user
                if int(request.POST[category_qty]) > 0 and int(request.POST[category_qty]) <= x.quantity:
                    req_detail.save()   
                    
            return render(request, 'receiverloginscreen.html' ,{'error' : 'Your Request details are saved !! ', 'dates': c , 'len': range(len(c)), 'flag':flag, 'e':e, 'cloths' : cloths, 'stationary': stationary, 'footwear': footwear })
        else:
            #if all required details are not filled by user
            return render(request, 'receiverloginscreen.html' ,{'error' : 'All details are required !! ','dates': c , 'len': range(len(c)), 'flag':flag, 'e':e, 'cloths' : cloths, 'stationary': stationary, 'footwear': footwear })
            
    else:
        if request.user.is_donor or request.user.is_volunteer:
            return render(request, 'index.html', {'message' : 'You are not authorized to go to receivers page !!'})

        return render(request, 'receiverloginscreen.html', {'dates': c , 'len': range(len(c)), 'flag': flag, 'e':e, 'cloths' : cloths, 'stationary': stationary, 'footwear': footwear })


@login_required(login_url='/login/')
def volunteerhome(request):
    collect = collection_drive.objects.all()
    donate = donation_drive.objects.all()
    d = {}
    i = 0
    c = {}
    j = 0
    c_flag = False
    d_flag = False
    dis_flag = True
    c_e = ' '
    d_e = ' '
    ob_volunteer = []
    c_by = collected_by.objects.all()
    d_by = donated_by.objects.all()
   
    for _ in c_by:
        if _.volunteer == request.user and _.date.date > date.today():
            if (_.date.date - date.today()).days <= 2 :
                ob_volunteer.append(_)
            c_flag = True
            c_e = '\n You are already registerd for upcomming collection drive on date '+ (_.date.date).strftime('%d-%m-%Y') + "\n" +' You cannot register in more than one collection drive at a time.'
            
    for _ in d_by:
       if _.volunteer == request.user and _.date.date > date.today():
           d_flag = True
           d_e = '\n You are already registerd for upcomming collection drive on date '+ (_.date.date).strftime('%d-%m-%Y') + "\n" +' You cannot register in more than one collection drive at a time.'
            
    for p in collect:
        if not(i < 3):
            break
        if p.date > date.today():
             d[i] = p
             i +=1
    for q in donate:
        if not(j < 3):
            break
        if q.date > date.today():
            c[j] = q
            j +=1
            
    date_d = donates_items_in.objects.all()
    p = {}
    for i in range(len(date_d)):
        curr_count = 1
        curr_user = date_d[i].donor
        if date_d[i].date not in p.keys():
            for j in range(i+1,len(date_d)):
                if curr_user != date_d[j].donor:
                    if date_d[i].date == date_d[j].date:
                        curr_count += 1
                        curr_user = date_d[j].donor
            p[date_d[i].date] = curr_count

    date_c = receives_items_in.objects.all()
    q = {}
    for i in range(len(date_c)):
        curr_count = 1
        curr_user = date_c[i].receiver
        if date_c[i].date not in q.keys():
            for j in range(i+1,len(date_c)):
                if curr_user != date_c[j].receiver:
                    if date_c[i].date == date_c[j].date:
                        curr_count += 1
                        curr_user = date_c[j].donor
            q[date_c[i].date] = curr_count

          
            
                   
    
    if request.method == "POST":
        if request.POST.get('collection_date',False) or request.POST.get('donation_date',False):
            if request.POST.get('collection_date',False):
                collected_by_details = collected_by()
                collected_by_details.volunteer = request.user
                collected_by_details.date = d[int(request.POST['collection_date'])]
                collected_by_details.save()
            if request.POST.get('donation_date',False):
                donated_by_details = donated_by()
                donated_by_details.volunteer = request.user
                donated_by_details.date = c[int(request.POST['donation_date'])]
                donated_by_details.save()
            return render(request,'volunteer-home.html',{'error' : 'Details saved !! ', 'collection_dates': d , 'donation_dates' : c, })
        
        else:
            return render(request,'volunteer-home.html',{'error' : 'Atleast one date is required !! ', 'collection_dates': d , 'donation_dates' : c, })
        #do something
        
    
    else:
        if request.user.is_receiver or request.user.is_donor:
            return render(request, 'index.html', {'message' : 'You are not authorized to go to volunteers page !!'})

        return render(request,'volunteer-home.html',{'collection_dates': d , 'donation_dates' : c, 'c_flag': c_flag, 'c_e':c_e,'d_flag': d_flag, 'd_e':d_e, 'donor_detail' : p, 'receiver_detail': q, 'dis_flag' : dis_flag})

@login_required(login_url='/login/')
def adminhome(request):
    collect = collection_drive.objects.all()
    d = {}
    i = 0
    for p in collect:
        d[i] = p
        i +=1


    donate = donation_drive.objects.all()
    c = {}
    j = 0
    for q in donate:
        c[j] = q
        j +=1

    env = Environment(loader=FileSystemLoader('./templates'))
    template = env.get_template("myreport.html")

    if request.method == "POST":
        if request.POST.get('collectiondrivedate',False):
            new_date = datetime.strptime(request.POST.get('collectiondrivedate'), '%Y-%m-%d')

            try:
                get_date = collection_drive.objects.get(date=new_date)
            except collection_drive.DoesNotExist:
                get_date = None

            if get_date is not None:
                return render (request,'admin.html', {'collection_dates': d, 'donation_dates' : c, 'DateAlreadyExists': True})
            else:
                collection_drive_ob = collection_drive()
                collection_drive_ob.date = new_date
                collection_drive_ob.save()
                return render (request,'admin.html', {'collection_dates': d, 'donation_dates' : c, 'NewDateAdded': True })

        elif request.POST.get('donationdrivedate',False):
            new_date = datetime.strptime(request.POST.get('donationdrivedate'),'%Y-%m-%d')

            try:
                get_date = donation_drive.objects.get(date=new_date)
            except donation_drive.DoesNotExist:
                get_date = None

            if get_date is not None:
                return render (request,'admin.html', {'collection_dates': d, 'donation_dates' : c, 'DateAlreadyExists': True})
            else:
                donation_drive_ob = donation_drive()
                donation_drive_ob.date = new_date
                donation_drive_ob.save()
                return render (request,'admin.html', {'collection_dates': d, 'donation_dates' : c, 'NewDateAdded': True })

        #To genrate collection drive reports
        elif request.POST.get('collection_date',False):
            collection_date_index = int(request.POST.get('collection_date',False))

            #if collection drive date has occured, we dont need to genrate report , just display report by fetching from database
            if(d[collection_date_index].date < date.today()):
                try :                         
                    f_ob = reports.objects.filter(collection_drive_date=d[collection_date_index])
                    f_ob = f_ob[0]
                    filepath = str(f_ob.filepath)
                except :
                    details = donates_items_in.objects.filter(date = d[collection_date_index])
                    if(len(details) == 0):
                        return render (request,'admin.html', {'collection_dates': d, 'donation_dates' : c, 'NoCollectionDrive' : True })
                    else:
                        columns=["Date","Donor","Address","Item","Qty"]
                        df = pd.DataFrame(columns=columns, dtype=float)
                        for _ in details:
                            dic = {}
                            dic["Date"]     = _.date.date
                            dic["Donor"]    = str(_.donor.first_name) +" "+ str(_.donor.last_name)
                            dic["Address"]  =  _.donor.address
                            dic["Item"]     = _.category.category
                            dic["Quantity"]      = int(_.quantity)
                            dic["Contact"]  = str(_.donor.contact_number)

                            df = df.append(dic, ignore_index= True)

                        collection_drive_report = pd.pivot_table(df, index=["Donor","Address","Contact", "Item"], values=["Quantity"])

                        template_vars = {"title" : "Collection Drive Report",
                             "national_pivot_table": collection_drive_report.to_html(), "date": d[collection_date_index].date}

                        html_out = template.render(template_vars)

                        HTML(string=html_out).write_pdf(MEDIA_ROOT + f'reports/collection drive reports/{d[collection_date_index].date}.pdf')

                        new_report = reports()
                        new_report.collection_drive_date = d[collection_date_index]
                        new_report.filepath =  f'reports/collection drive reports/{d[collection_date_index].date}.pdf'
                        new_report.save()


                        f_ob = reports.objects.filter(collection_drive_date=d[collection_date_index])
                        f_ob = f_ob[0]
                        filepath = str(f_ob.filepath)

                            

                        fs = FileSystemStorage(MEDIA_ROOT)
                        with fs.open(filepath) as pdf:
                            response = HttpResponse(pdf, content_type='application/pdf')
                            response['Content-Disposition'] = 'attachment; filename= "{}.pdf"'.format(d[collection_date_index].date)

                        return response



                fs = FileSystemStorage(MEDIA_ROOT)
                with fs.open(filepath) as pdf:
                    response = HttpResponse(pdf, content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename= "{}.pdf"'.format(d[collection_date_index].date)

                return response

            #if collection drive is pending, we need to genrate report as it may contain updation, hence delete old record form database
            #and add new record
            else:
                details = donates_items_in.objects.filter(date = d[collection_date_index])
                if(len(details) == 0):
                    return render (request,'admin.html', {'collection_dates': d, 'donation_dates' : c, 'NoDonor' : True })
                columns=["Date","Donor","Address","Item","Qty"]
                df = pd.DataFrame(columns=columns, dtype=float)
                for _ in details:
                    dic = {}
                    dic["Date"]     = _.date.date
                    dic["Donor"]    = str(_.donor.first_name) +" "+ str(_.donor.last_name)
                    dic["Address"]  =  _.donor.address
                    dic["Item"]     = _.category.category
                    dic["Quantity"]      = int(_.quantity)
                    dic["Contact"]  = str(_.donor.contact_number)

                    df = df.append(dic, ignore_index= True)

                collection_drive_report = pd.pivot_table(df, index=["Donor","Address","Contact", "Item"], values=["Quantity"])

                template_vars = {"title" : "Collection Drive Report",
                     "national_pivot_table": collection_drive_report.to_html(), "date": d[collection_date_index].date}

                html_out = template.render(template_vars)

                HTML(string=html_out).write_pdf(MEDIA_ROOT + f'reports/collection drive reports/{d[collection_date_index].date}.pdf')

                try:
                    old_entry = reports.objects.get(collection_drive_date=d[collection_date_index])
                    old_entry.delete()
                except:
                    pass

                new_report = reports()
                new_report.collection_drive_date = d[collection_date_index]
                new_report.filepath =  f'reports/collection drive reports/{d[collection_date_index].date}.pdf'
                new_report.save()


                f_ob = reports.objects.filter(collection_drive_date=d[collection_date_index])
                f_ob = f_ob[0]
                filepath = str(f_ob.filepath)

                    

                fs = FileSystemStorage(MEDIA_ROOT)
                with fs.open(filepath) as pdf:
                    response = HttpResponse(pdf, content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename= "{}.pdf"'.format(d[collection_date_index].date)

                return response

        #to genrate donation drive reports
        else:
            donation_date_index = int(request.POST.get('donation_date',False))

            #if collection drive date has occured, we dont need to genrate report , just display report by fetching from database
            if(c[donation_date_index].date < date.today()):
                try :                         
                    f_ob = reports.objects.filter(donation_drive_date=c[donation_date_index])
                    f_ob = f_ob[0]
                    filepath = str(f_ob.filepath)
                except :
                    details = receives_items_in.objects.filter(date = c[donation_date_index])
                    if(len(details) == 0):
                        return render (request,'admin.html', {'collection_dates': d, 'donation_dates' : c, 'NoDonationDrive' : True })
                    else:
                        columns=["Date","Receiver","Address","Item","Qty"]
                        df = pd.DataFrame(columns=columns, dtype=float)
                        for _ in details:
                            dic = {}
                            dic["Date"]     = _.date.date
                            dic["Receiver"]    = str(_.receiver.ngo_name)
                            dic["Address"]  =  _.receiver.address
                            dic["Item"]     = _.category.category
                            dic["Quantity"]      = int(_.quantity)
                            dic["Contact"]  = str(_.receiver.contact_number)

                            df = df.append(dic, ignore_index= True)

                        donation_drive_report = pd.pivot_table(df, index=["Receiver","Address","Contact", "Item"], values=["Quantity"])

                        template_vars = {"title" : "Donation Drive Report",
                             "national_pivot_table": donation_drive_report.to_html(), "date": c[donation_date_index].date}

                        html_out = template.render(template_vars)

                        HTML(string=html_out).write_pdf(MEDIA_ROOT + f'reports/donation drive reports/{c[donation_date_index].date}.pdf')

                        new_report = reports()
                        new_report.donation_drive_date = c[donation_date_index]
                        new_report.filepath =  f'reports/donation drive reports/{c[donation_date_index].date}.pdf'
                        new_report.save()


                        f_ob = reports.objects.filter(donation_drive_date=c[donation_date_index])
                        f_ob = f_ob[0]
                        filepath = str(f_ob.filepath)

                            

                        fs = FileSystemStorage(MEDIA_ROOT)
                        with fs.open(filepath) as pdf:
                            response = HttpResponse(pdf, content_type='application/pdf')
                            response['Content-Disposition'] = 'attachment; filename= "{}.pdf"'.format(c[donation_date_index].date)

                        return response

                fs = FileSystemStorage(MEDIA_ROOT)
                with fs.open(filepath) as pdf:
                    response = HttpResponse(pdf, content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename= "{}.pdf"'.format(c[donation_date_index].date)

                return response

            #if collection drive is pending, we need to genrate report as it may contain updation, hence delete old record form database
            #and add new record
            else:
                details = receives_items_in.objects.filter(date = c[donation_date_index])
                if(len(details) == 0):
                    return render (request,'admin.html', {'collection_dates': d, 'donation_dates' : c, 'NoReceiver' : True })
                columns=["Date","Receiver","Address","Item","Qty"]
                df = pd.DataFrame(columns=columns, dtype=float)
                for _ in details:
                    dic = {}
                    dic["Date"]     = _.date.date
                    dic["Receiver"]    = str(_.receiver.ngo_name)
                    dic["Address"]  =  _.receiver.address
                    dic["Item"]     = _.category.category
                    dic["Quantity"]      = int(_.quantity)
                    dic["Contact"]  = str(_.receiver.contact_number)

                    df = df.append(dic, ignore_index= True)

                donation_drive_report = pd.pivot_table(df, index=["Receiver","Address","Contact", "Item"], values=["Quantity"])

                template_vars = {"title" : "Donation Drive Report",
                     "national_pivot_table": donation_drive_report.to_html(), "date": c[donation_date_index].date}

                html_out = template.render(template_vars)

                HTML(string=html_out).write_pdf(MEDIA_ROOT + f'reports/donation drive reports/{c[donation_date_index].date}.pdf')

                try:
                    old_entry = reports.objects.get(donation_drive_date=c[donation_date_index])
                    old_entry.delete()
                except:
                    pass

                new_report = reports()
                new_report.donation_drive_date = c[donation_date_index]
                new_report.filepath =  f'reports/donation drive reports/{c[donation_date_index].date}.pdf'
                new_report.save()


                f_ob = reports.objects.filter(donation_drive_date=c[donation_date_index])
                f_ob = f_ob[0]
                filepath = str(f_ob.filepath)

                    

                fs = FileSystemStorage(MEDIA_ROOT)
                with fs.open(filepath) as pdf:
                    response = HttpResponse(pdf, content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename= "{}.pdf"'.format(c[donation_date_index].date)

                return response



    

    return render (request,'admin.html', {'collection_dates': d, 'donation_dates' : c })




    