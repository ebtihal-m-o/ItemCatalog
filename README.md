# Item-Catalog
Udacity Item Catalog project
## Project Overview
This project is for develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system(googel). Registered users will have the ability to post, edit and delete their own prodact.
## Why This Project?
Modern web applications perform a variety of functions and provide amazing features and utilities to their users; but deep down, it’s really all just creating, reading, updating and deleting data. **This project** is for combine learning  knowledge on building dynamic websites with persistent data storage to create a web application that provides a compelling service to your users.
## How to complete this project?
 1.  Install [Vagrant](https://www.vagrantup.com/downloads.html) and [VirtualBox](https://www.virtualbox.org/wiki/Downloads).
 2.  Clone the [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) .
 3.  Launch the Vagrant VM (vagrant up).
 4.  Write your Flask application locally in the vagrant/catalog directory (which will automatically be synced to /vagrant/catalog within the VM).
 5.  Run your application within the VM (vagrant/catalog/application.py).
 6.  Access and test your application by visiting  [http://localhost:5000](http://localhost:5000/)  locally.
## Using Google Login
To get the Google login working there are a few additional steps:
1.  Go to  [Google Dev Console](https://console.developers.google.com/)
2.  Sign up or Login if prompted
3.  Go to Credentials
4.  Select Create Crendentials > OAuth Client ID
5.  Select Web application
6.  Enter name 'Item-Catalog'
7.  Authorized JavaScript origins = '[http://localhost:5000](http://localhost:5000/)'
8.  Authorized redirect URIs = '[http://localhost:5000/login](http://localhost:5000/login)' && '[http://localhost:5000/gconnect](http://localhost:5000/gconnect)'
9.  Select Create
10.  Copy the Client ID and paste it into the  `data-clientid`  in login.html
11.  On the Dev Console Select **Download JSON**
12.  Rename JSON file to **client_secrets.json**
13.  Place JSON file in item-catalog directory that you cloned from here
14.  Run application using  `python vagrant/catalog/application.py`
