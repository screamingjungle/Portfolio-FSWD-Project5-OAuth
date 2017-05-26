CACHE - wrappers e.g.
http://docs.sqlalchemy.org/en/latest/orm/examples.html#examples-caching


TODO:
- on category deletion, remove category_ids from items



You will develop an application that provides a list of items within a variety of collections as well as provide a user registration and authentication system. 
Registered users will have the ability to post, edit and delete their own items.

```
pip install -r requirements.txt

pip2 install  -r requirements.txt
``` 

--------------------------------------------------------------------
# Item Catalog

![](http://progressed.io/bar/30?title=Progress)

## What is this?
This is the Item Category project \#5 from the [Udacity Full Stack Nanodegree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).
A user can register and login with their Google and Facebook account.
Registered users can create new collections, categories and items.

The project consists of:

- HTML
- CSS
- Python implementing Flask framework with Jinja2 templating
- Google and Facebook OAuth2 accounts (you will need to configure your own accounts to use this)
- SQLite database (with initial seed/dummy data)

___

### Getting started

## Virtual Box and Vagrant

This provisions a working Virtual Box environment (virtual machine = VM) using Vagrant. Easy!
Udacity has a [guide to help](https://www.udacity.com/wiki/ud197/install-vagrant)

1 Install [Vagrant]((http://www.vagrantup.com/downloads.html) and [Virtual Box](https://www.virtualbox.org/wiki/Downloads)
2 Clone the [github repository](https://github.com/screamingjungle/Portfolio-FSWD-Project5-OAuth)
3 CD into the project root directory - where the Vagrantfile is found.
Run the following:terminal/console command to provision and configure your Virtual environment.
```
vagrant up
```
4 Connect to the VM via SSH from your terminal/console.
```
vagrant ssh
```
If you are on windows you may need a SSH client. e.g. [CMDER](http://cmder.net/)

5 Once logged into the VM console, go to the following directory:
```
cd /vagrant/catalog/
```
6 Run the Python code.
```
python shopfront.py
```
The first time this code is run a sample SQLite database will be created with dummy data in a file called 'shopfrontcatalog.db'.
Images are also copied into the 'catalog/shopfront/img/' directory.
The seed config info can be found in 'catalog/shopfront/database_seed.py'.

7 Check the http port the webservice is running on and fire up your web browser to http://localhost:5000 (or wherever that port is pointing to)



* Once finished with the VM you can stop it - escape the SSH console (Ctrl-D) and then stop Vagrant.
```
vagrant halt
```
To reset back to the starting point you can destroy the VM:
```
vagrant destroy
```


### Features

## Cross-site Request Forgery
Read more about CSRF [here](https://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF))

This application uses [Flask-SeaSurf](https://flask-seasurf.readthedocs.io/en/latest/), which is installed when you provisioned your VM via Vagrant above.

## JSON Endpoints
There are two endpoints currently defined.
1 [http://localhost:5000/catalog.json](http://localhost:5000/catalog.json) or [http://localhost:5000/item/json](http://localhost:5000/item/json)

This shows all catalog items for the logged in user (or everything for Admin).

2 [http://localhost:5000/search_json/<query>](http://localhost:5000/search_json/<query>)
query: this will do a search for (partial) matches in the Item name or tags.
This is used in the search feature found in the menu.

## Search
Search for products. Partial matches against Item names and Item tags.
(http://localhost:5000/search/abc)[http://localhost:5000/search/abc]

## Messages
Shows messages to user. This may include the following:
- items that are not linked to Collections or Categories

## Collections
If an item is not linked to a collection, it is in fact linked to an 'orphaned'
collection with id:1. This is visible to Admin.
An 'archive' collection also exists with id:2. This is not visible to public.

### File Structure
Brief overview of the files.
```
├── client_secrets.json     #Put your Google secrets in here
├── fb_client_secrets.json  #Put your Facebook secrets in here
├── shopfront.py  #The main program launcher
├── shopfrontcatalog.db  #database for the app.
├── shopfront     #application directory and code
│   ├── db #Database-related modules here plus seed data
│   │   └── seed_images #copied to 'img' directory when creating new db
│   ├── handlers  #View modules including decorators and functions helper
│   ├── img       #images for catalog items, favicon
│   ├── static    #CSS, Javascript, images used for UI
│   └── templates #HTML files using Jinja2 templating system
├── README.md
└── Vagrantfile   #Needed to get your VM up and running


---

## Sources

* Udacity Discussion Board
* [Pep8 Python Style Guide](https://www.python.org/dev/peps/pep-0008/)
* [Udacity's Fullstack Foundations course](https://www.udacity.com/course/full-stack-foundations--ud088)
* [Udacity Authentication & Authorization: OAuth course](https://www.udacity.com/course/authentication-authorization-oauth--ud330)
* [Item Catalog: Getting Started Guide](https://docs.google.com/document/d/1jFjlq_f-hJoAZP8dYuo5H3xY62kGyziQmiv9EPIA7tM/pub?embedded=true)


