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
import pandas as pd
import numpy as np
from jinja2 import Environment, FileSystemLoader
from django.http import HttpResponse
# from weasyprint import HTML


User = get_user_model()


def contact(request):
    return render(request,'contact.html')

def home(request):
    return render(request, 'index.html')

def aboutus(request):
    return render(request, 'aboutus.html')

def demo(request):
    return render(request, 'admin.html')

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
                                                contact_number = request.POST['mobile'],is_donor= donor_check, is_volunteer = volunteer_check)
                auth.login(request, user)
                return redirect('home')
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
                                                    contact_number = request.POST['mobile'],is_donor= donor_check, is_volunteer = volunteer_check, is_receiver = ngo_check)
                    auth.login(request, user)
                    return redirect('home')
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
                return redirect('receiverhome')
        else:
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
        
@login_required
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
        return render(request, 'donorloginscreen.html', {'dates': c , 'len': range(len(c)), 'flag': flag, 'e':e })
    
@login_required
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
        if cs.category == 'Cloths':
            cloths = cs.quantity
        if cs.category == 'Stationary':
            stationary = cs.quantity
        if cs.category == 'Footwear':
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
        return render(request, 'receiverloginscreen.html', {'dates': c , 'len': range(len(c)), 'flag': flag, 'e':e, 'cloths' : cloths, 'stationary': stationary, 'footwear': footwear })


@login_required
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
    
    for _ in date_d:
        curr_count = 1
        curr_user = _.donor
        for x in date_d:
            if curr_user != x.donor:
                curr_count += 1
        p[_.date] = curr_count


    print(p)
                
            
                   
    
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
        return render(request,'volunteer-home.html',{'collection_dates': d , 'donation_dates' : c, 'c_flag': c_flag, 'c_e':c_e,'d_flag': d_flag, 'd_e':d_e, 'donor_detail' : p, 'dis_flag' : dis_flag})


def adminhome(request):
    collect = collection_drive.objects.all()
    d = {}
    i = 0
    for p in collect:
        if not(i < 3):
            break
        if p.date > date.today():
             d[i] = p
             i +=1


    donate = donation_drive.objects.all()
    c = {}
    j = 0
    for q in donate:
        if not(j < 3):
            break
        if q.date > date.today():
            c[j] = q
            j +=1


    columns=["Date","Donor","Address","Item","Qty"]
    df = pd.DataFrame(columns=columns, dtype=float)
    details = donates_items_in.objects.all()
    for _ in details:
        dic = {}
        dic["Date"]     = _.date.date
        dic["Donor"]    = str(_.donor.first_name) +" "+ str(_.donor.last_name)
        dic["Address"]  =  _.donor.address
        dic["Item"]     = _.category.category
        dic["Qty"]      = _.quantity
        df = df.append(dic, ignore_index= True)

    donation_drive_report = pd.pivot_table(df, index=["Donor","Address", "Item"], values=["Qty"])

    print(donation_drive_report.head())

    env = Environment(loader=FileSystemLoader('./templates'))
    template = env.get_template("myreport.html")

    template_vars = {"title" : "Donation Drive Report",
                 "national_pivot_table": donation_drive_report.to_html()}

    html_out = template.render(template_vars)


    if request.method == "POST":
        if request.POST.get('collection_date',False):
            return HttpResponse(html_out)


    

    return render (request,'admin.html', {'collection_dates': d, 'donation_dates' : c })