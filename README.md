# HelpingHands
**( College project. Still under development )**

Live Demo : http://lendyourhand.herokuapp.com/

How to run project :

          * Install pipenv using command :
                    pip install pipenv

          * Goto to the directory where you are going to pull this repo, and create a virtual environment.
            Use below command to do it witn pipenv ( there are other means you can use them too ).
                    virtualenv .

          * Activate the virtual environment just created, using command :
                    .Scripts\activate   (On windows)
                    On linux, move to bin folder and execute the command:
                    source .\activate

          * Pull this repo and install requirements.txt , using command :
                    pip install -r requirements.txt

          * Now using manage.py , start your server, using command :
                    python manage.py runserver

          Note : 1. If you are using windows you may need to start Mysql server using web server application like XAMPP.
                    On linux you and do it by using command :
                        sudo /etc/init.d/mysql start

                  2. When running project for the first time, you will need to make migrations to the database. 
                     This will create tables in the database. Command to do it is :
                        python manage.py makemigrations
                        python manage.py migrate

                  3. You may need to create a django superuser which will give access to django admin page.
                     To do so, use command :
                        python manage.py createsuperuser
                          Enter desired username and password
                
                          

