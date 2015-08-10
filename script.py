#!/usr/bin/env python
 
"""
Created on 24/10/2013
version 1.2
@author: n3k
 
"""
 
import sys, os
import string
from lxml import html
from lxml.html import parse
import re
from urlparse import urlparse
import threading
import Queue
import time
 
 
class Book(threading.Thread):
 
    def __init__(self, queue, fileName):
        threading.Thread.__init__(self)
        self.queue = queue
	self.fileName = fileName
       
    def run(self):
        url = self.queue.get()
        try:
            tree = html.parse(url)
            links = tree.xpath("//td/a/@href")
            title = tree.xpath("//h1/text()")
            t = title[0].replace("&","and")
            t = re.sub('[^a-zA-Z0-9\n\.\+]', ".", t)
            t += ".pdf"
            link = links[0]
            if link[:7] == 'http://':
                final_link = link
            elif link[0] == "/":
                final_link = "http://it-ebooks.info/" + link
	    bookFileName = t;
	    print "Verifying "+t;
	    os.system("echo '"+"Verifying "+t+"' >> "+self.fileName)
	    if not os.path.isfile(bookFileName):
		comment = "--> No such file "+t
		print comment;
		os.system("echo '"+comment+"' >> "+self.fileName)
		command = "wget --referer="+url+" --output-document="+t +" "+final_link
		os.system(command)		
        except:
            f = open("url.errors.txt", "a")
            f.writelines("Error with URL:" + url)
            f.close()
        self.queue.task_done()
 
               
def download_all():
    timeToday = time.strftime("%d_%m_%Y")
    fileName = "report_"+timeToday
    title = "Comenzando corrida de hoy - "+timeToday
    os.system("echo '"+title+"' >> "+fileName)
    start_url = "http://it-ebooks.info/publisher/"
    for publisher in range(1,16+1):
        current_publisher = start_url + str(publisher)+"/"
	print current_publisher
        tree = html.parse(current_publisher+"/")
	print tree
        name = tree.xpath("//h1/text()")
	print name
        n = name[0]
	print "Exists dir ?"+n
	if not os.path.exists(n):
	    os.makedirs(n)
    	    print "Creating dir "+t +" "+final_link;
        os.chdir(n)
        download_page(current_publisher, "1", "../"+fileName)
        os.chdir("..")
	
 
 
books_processed = set()
 
def download_page(current_publisher, page, fileName):
    page_to_download = current_publisher + "/page/" + page + "/"
    os.system("echo '"+page_to_download+"' >> "+fileName)
    print page_to_download
    tree = html.parse(page_to_download)        
    links = tree.xpath("//a/@href")
    links_titles = tree.xpath("//a/@title")
    queue = Queue.Queue()
    for link in links:
        if re.match("/book.*", link) and link not in books_processed:
            books_processed.add(link)
            worker = Book(queue, fileName)
            job = "http://it-ebooks.info/"+link
	    os.system("echo 'processing "+job+"' >> "+fileName)
            queue.put(job)
            worker.setDaemon(False)
            worker.start()                             
    queue.join()
    if bool(sum(map(lambda x: x in ["Next page"], links_titles))):
        download_page(current_publisher, str(int(page) + 1), fileName)
 
download_all()
