# Multiprocessing-SSH

Multiprocessing-SSH based execution where user can provide list of hostname and get details about each host

Source Code:
------------

`<https://github.com/BHushanRathod/Multiprocessing-SSH>`_


Installation and Usage
======================

Download the souce code::
       
    $ git clone https://github.com/BHushanRathod/Multiprocessing-SSH.git
    $ cd hostname
   
Activate the Virtual Environment::

    source ~/path/to/ve/bin/activate

Install the Dependencies::

    pip install -r requirements.txt

Run Migrations (Not required)::
    
    ./manage.py makemigrations
    ./manage.py migrate
    
Run TestCases::

    python manage.py test
        
* Steps to follow:
    
    * Install the requirements from requirements.txt.
    * Update the hostname_list.txt while with list of hosts each on new line
    * Create postgres database with `key_vals` table and (hostname, key, user_name) columns
    * Run python hostname.py.
    * Read the menu. First add the private key into database. 
    * To encrypt the private file and add to database, select option 1 when prompted::
    * Enter the full path of the private key, then enter the password to encrypt it.
    * Keep the passphrase stored at secure location, or try to remember the key. Once passphrase lost, you can not retrieve the key.
    * Once key stored in database, select the option 2. This is SSH into all the host and will print hostname and CPU cores.
