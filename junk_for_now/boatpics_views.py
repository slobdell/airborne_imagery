#TODO:  Fix eliminate repeat days
#TODO  Redo supersetting such that the exercise pooling is done before filter by muscle group

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.db import connection
from django.db.models import Max
from django.conf.urls.defaults import *

from django.contrib.sessions.models import Session
from django import http
###for youtube videos
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

import ImageDraw

from django.template.defaultfilters import stringfilter
from django import template
import re
import os, sys
import math
from myproject.boatpix.forms import *
from myproject.boatpix.models import *
from django.db.models import Q
#from strengthgoal.models import *
from django.core.mail.message import EmailMessage

import random
import datetime
from datetime import timedelta
from datetime import date

from django.core import serializers
from django.utils import simplejson

import time
from ftplib import FTP
from StringIO import StringIO


from PIL import Image
from PIL.ExifTags import TAGS
import Image, ImageEnhance
import collections





host="70.89.99.61"
ftpPort="21"
username="administrator"
password="kwbnd1"
#username="testuser"
#password="password"

#for production, change lobdellbrothers.com URL to boatpix.com
#freeOrder=True
#emailTo=boatpix guys
#email all contact forms to boatpix guys
#imageDirectoryFTP="/BoatPix_Web_Access/"
imageDirectoryFTP=("/NAS5/","/NAS3/","/NAS1/","/NAS4/","/NAS5/", "/NAS6/")
#haarcascade_frontalface_alt.xml"))
attachImage=True



def debug(inText):
  currentTime=datetime.datetime.now()
  f = open('/home/aesg/webapps/boatpix/myproject/debug.txt','a')
  f.write(currentTime.__str__()+": "+inText+"\n") # ... etc.
  f.close()





def get_exif_data_from_image(inImage):
    """Get embedded EXIF data from image file."""
    ret = {}
    try:
        img = inImage
        if hasattr( img, '_getexif' ):
            exifinfo = img._getexif()
            if exifinfo != None:
                for tag, value in exifinfo.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
    except IOError:
        print 'IOERROR ' + fname
    return ret
def isFile(ftpFile, ftpObj):
  ftp=ftpObj
  current=ftp.pwd()  #get the current path name
  try:
    ftp.cwd(ftpFile)  #set the current path name
  except:
    ftp.cwd(current)
    return True
  ftp.cwd(current)
  return False


#startTime=datetime.now()
#endTime=datetime.now()
#myTimeDelta= endTime-startTime
#print myTimeDelta.seconds
appendString="_resized_copy_read_only"
def deletePicturesFromFTPServer():
  startTime=datetime.datetime.now()
  allFiles=[]
  def traverse(directory):
    if appendString in directory:
      return
    print "traversing "+directory
    deleteCounter=0
    files=[]
    toTraverse=[]
    try:
      files=set(ftp.nlst(directory))
    except:# Exception, e:
#      exc_type, exc_obj, exc_tb = sys.exc_info()
#      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#      message=(exc_type, fname, exc_tb.tb_lineno)
      print "error listing directory"
    for f in files:
      deleteCounter+=1
      #print "checking "+f
      if deleteCounter %100==0:
        pass
        #print "Garbage Collecting, "+deleteCounter.__str__()+" files processed"
	#gc.collect()
      if ".jpg" in f.lower() and not appendString in f.lower():
        #allFiles.extend(files)
        allFiles.append(f)
      elif appendString in f.lower():
        pass
      elif not isFile(f, ftp):
        #traverse(f)
        toTraverse.append(f)
    files=[]
    del files
    for iterator in toTraverse:
      traverse(iterator)



  ftp=FTP()
  ftp.connect(host, port=ftpPort)
  ftp.login(username, password)
  print "authenticated"
  for dir in imageDirectoryFTP:
    traverse(dir)
  toRemove=[]
  validFiles=[]
  allFiles=set(allFiles)
  counter=0
  allM=Map.objects.all()
  for iterator in allM:
    counter+=1
    if counter %1000==0:
      print "checked "+counter.__str__()+" map objects for delection"
    validFiles.append(iterator.watermarkName)
    if not iterator.ftpName in allFiles:  #file has been removed, DELETE
      os.system('rm '+ imageDirectory+iterator.watermarkName)
      os.system('rm '+ imageDirectory+"thumbnail-"+iterator.watermarkName)
      print iterator.ftpName + " is not in the directory listing; deleting."
#      print "deleting "+iterator.watermarkName
      toRemove.append(iterator)
  validFiles=set(validFiles)
  for iterator in toRemove:
    iterator.delete()
  ftp.quit()
  presentFiles=set(os.listdir(imageDirectory))
  counter=0
  for iterator in allM:
    counter+=1
    if counter %1000==0:
      print "checked "+counter.__str__()+" map objects for delection"
    if not iterator.watermarkName in presentFiles:
      print"deleting "+iterator.watermarkName+" Map object"
      toRemove.append(iterator)
  for filename in presentFiles:
    if ".png" in filename:
      pass
    else:
      if not filename in validFiles and not filename.replace("thumbnail-","") in validFiles:
        print filename + " is an invalid file"
        os.system('rm '+imageDirectory+filename)
  for iterator in toRemove:
    try:
      iterator.delete()
      print "deleting "+iterator.ftpName+"\n"
    except:
      print "error deleting "+iterator.ftpName+"\n"
  endTime=datetime.datetime.now()
  myTimeDelta= endTime-startTime
  return myTimeDelta.seconds



import gc
import urllib
def getLatLonFromKeyword(keyword):
  url = 'http://maps.google.com/?q=' + urllib.quote(keyword) + '&output=js'
  xml = urllib.urlopen(url).read()
  if '<error>' in xml:
    print '\nGoogle cannot interpret the address.'
  else:
    lat,lng = 0.0,0.0
    center = xml[xml.find('{center')+10:xml.find('}',xml.find('{center'))]
    center = center.replace('lat:','').replace('lng:','').replace('at:','')
    lat,lng = center.split(',')
    return lat, lng



def parseLine(line):
    pattern = r'.* ([A-Z|a-z].. .. .....) (.*)'
    found = re.match(pattern, line)
    if (found is not None):
        return found.groups()
    return None








import sched, time, threading
startTime2=datetime.datetime.now()
picturesWritten=0
picturesForRate=0
def do_something(sc, incrementor):
    global startTime2
    global picturesForRate
    currentTime=datetime.datetime.now()
    timeDelta=currentTime-startTime2
    timeDelta=float(timeDelta.seconds)
    if timeDelta!=0:
        rate=int(3600.0*float(picturesForRate)/timeDelta)
        print "\n******Current Rate is "+rate.__str__()+" pictures per hour, "+ picturesWritten.__str__()+" written******\n"

    startTime2=datetime.datetime.now()
    picturesForRate=0
    incrementor+=1
    global timeout
    if incrementor>=float(timeout)/60-1:
      print "Killing the clock process because of timeout"
      return
    sc.enter(60, 1, do_something, (sc, incrementor))





allThreads=[]
maxThreads=6
timeout=3500000
def imageHandlingThread(ftpObject, watermark, filename, ftpDict):
  ftp=ftpObject
  mark=watermark
  global picturesWritten
  global picturesForRate
  r=StringIO()
#  print "SBL downloading "+filename
  ftp.retrbinary('RETR '+filename, r.write)
  img=None
  try:
    img=Image.open(StringIO(r.getvalue()))
  except:
    print "Error on save "+filename
    pass #not an image file
  if img!=None:
    print "saving "+filename
    handleImage(img, filename.replace(appendString,""), mark)
    picturesWritten+=1
    picturesForRate+=1
  ftpDict[ftpObject]=False#Free it up

def refreshPicturesFromFTPServer(secondsElapsed=0, lookForGPS=False):
  global timeout
  startTime=datetime.datetime.now()-timedelta(0, secondsElapsed)
  if False:
    s = sched.scheduler(time.time, time.sleep)
    s.enter(60, 1, do_something, (s,1))
    timerThread=threading.Thread(target=s.run)
    timerThread.start()

  counter=0
  def refreshExistingFiles2(currentDirectory):
    for dir in imageDirectoryFTP:
      currentDirectory=currentDirectory.replace(dir, "")
      if len(currentDirectory)==0:
        currentDirectory=dir
    currentDirectory=currentDirectory.replace("\\","/").replace("/", " ").replace(appendString, "")
    allM=list(Map.objects.filter(ftpFolder=currentDirectory).values_list('ftpName', flat=True))
    return set(allM)

#  def refreshExistingFiles(currentFileName):
#    myExistingFiles=[]
#    #allM=Map.objects.filter(ftpName__contains=currentFileName)
#    allM=Map.objects.filter(ftpName__contains=currentFileName).values_list('ftpName', flat=True)
#    for iterator in allM:
#      myExistingFiles.append(iterator.lower())
#    return set(myExistingFiles)

  def traverse(directory, innerCounter=counter, inMark=None):
    if not appendString in directory and not directory in imageDirectoryFTP:
      return  #need to change this if sub directories end up having stuff
    mark=inMark
    if mark==None:
      mark = Image.open(imageDirectory+'watermark.png')
    print "STARTING TRAVERSE of "+directory
    files=[]
    toTraverse=[]
    if True:
      originalFiles=None
      try:
        originalFiles=list(ftp.nlst(directory))
        #random.shuffle(originalFiles)
        originalFiles=set(originalFiles)
      except:
        print "FAILED at "+directory
        originalFiles=set(ftp.nlst(directory))
      from random import shuffle
      import operator
      if "gpscoords.txt" in directory.lower():
        print "PISS"
        return
      #shuffle(files)
#      files=set(files)
      ftp.cwd(directory)#hhhh
      lines=[]
#      ftp.retrbinary('RETR '+f, r.write)
      ftp.retrlines('LIST', lines.append)
      now=datetime.datetime.now()
      currentYear=now.year.__str__()
      results=[]
      for iterator in lines:
#        fileName=iterator[59:len(iterator)]
        result=parseLine(iterator)#result[1] is the filename
        if result!=None and len(result)==2:
          try:
            dateString=""
            if ':' in result[0]:
              dateString= result[0][0:7]+' '+currentYear
            else:
              dateString= result[0]
            dateObj=datetime.datetime.strptime(dateString, "%b %d %Y")
            newTuple=[]
            newTuple.append(dateObj)
            newTuple.append(result[1])
            results.append(newTuple)
            #print dateObj
          except:
#            print iterator
            pass #need to figure out why this didn't work

      lines=ftpSelectionSort(results)
      files=[]
      for iterator in lines:
         #ok so this worked
        files.append(directory+iterator[1])
      for iterator in originalFiles:
        if not iterator in files:
          files.append(iterator)
          print "appending "+iterator
      del lines
    else:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      message=(exc_type, fname, exc_tb.tb_lineno)
      print message
    existingFiles=refreshExistingFiles2(directory)
    for f in files:
      now=datetime.datetime.now()
      myTimeDelta= now-startTime
      totalSeconds=myTimeDelta.seconds
      if totalSeconds>timeout:
        print "Exiting program due to timeout"
        return
      if innerCounter%10==0:
	gc.collect()
	print ".",
        innerCounter+=1
      if not '.' in f:
        toTraverse.append(f+'/') #it's a folder
      else:
        if ".jpg" in f.lower() and not appendString in f.lower():
          pass  #what is this even for???  I don't even know now
#        existingFiles=refreshExistingFiles(f.replace(appendString,""))
        if f.replace(appendString,"") in existingFiles:
          #print "case1, file already exists"
          #print "exists already: "+f
          pass
        elif ".lnk" in f.lower() or ".rtf" in f.lower() or "thumbs.db" in f.lower():
          print "case 2, we don't care about this file"
        elif appendString in f and ".jpg" in f.lower():
          innerCounter+=1
          #print f
#XXXXXXXXXXXXXX

          while len(allThreads)>=maxThreads:
            time.sleep(0.2)
            for iterator in allThreads:
                if not iterator.isAlive():
                    allThreads.remove(iterator)
#    ftpArray.append(newFTP)
#    ftpDict[newFTP]=Failse
          ftpObjectToUse=None
          for key, value in ftpDict.items():
            if value==False:
              ftpObjectToUse
              ftpObjectToUse=key
              ftpDict[key]=True
              processThread = threading.Thread(target=imageHandlingThread, args=(ftpObjectToUse, mark, f, ftpDict))
              allThreads.append(processThread)
              processThread.start()
              time.sleep(0.2)
              break

#XXXXXXXXXXXXXX
#          imageHandlingThread(ftp, mark, f)
        #elif ".jpg" in f.lower() or isFile(f, ftp):
        #  pass  #ignore the jpg files that are big

        else: #it's a folder
          if ".txt" in f:
            print "fucked up somewhere"
          else:
            toTraverse.append(f+'/') #it's a folder
        #print "This is a folder: "+f
        #traverse(f, innerCounter, mark)
    files=[]
    del files
    for iterator in toTraverse:
      now=datetime.datetime.now()
      myTimeDelta= now-startTime
      totalSeconds=myTimeDelta.seconds
      if totalSeconds>timeout:
        print "Exiting program due to timeout"
        return
      traverse(iterator, innerCounter, mark)

  def traverseGPS(directory):
    print "GPS STARTING TRAVERSE of "+directory
    if appendString in directory:
      return
    #files=[directory+'gpsCoords.txt']
    files=ftp.nlst(directory)
    #from random import shuffle
    #shuffle(files)
    for f in files:
      now=datetime.datetime.now()
      myTimeDelta= now-startTime
      totalSeconds=myTimeDelta.seconds
      if totalSeconds>3500:
        return
      if ".jpg" in f.lower():
        pass
      elif ".txt" in f.lower():# or isFile(f, ftp):
        if "gpscoords.txt" in f.lower():
          try:
            lines=[]
            ftp.retrlines("RETR "+f, lines.append)
            if ',' in lines[0]:
              lines=lines.split(",")
            lat=0
            lon=0
            latInMinsSeconds=""
            lonInMinsSeconds=""
            if not ',' in lines[0] and not '.' in lines[0]:
              lat, lon=getLatLonFromKeyword(lines[0])
            else:
              latInMinsSeconds=lines[0].split(".")
              lonInMinsSeconds=lines[1].split(".")

              if len(latInMinsSeconds) >2:
                lat=abs(float(latInMinsSeconds[0]))+float(latInMinsSeconds[1])/60.0+float(latInMinsSeconds[2])/3600.0
                lon=abs(float(lonInMinsSeconds[0]))+float(lonInMinsSeconds[1])/60.0+float(lonInMinsSeconds[2])/3600.0
                if float(latInMinsSeconds[0])<0:
                  lat*=-1
                if float(lonInMinsSeconds[0])<0:
                  lon*=-1
              else:
                lat=float(lines[0])
                lon=float(lines[1])
            lat=float(lat)
#round(lat, 6)
            lon=float(lon)
  #round(lon, 6)
            allM=list(Map.objects.filter(ftpName__contains=directory))
            for iterator in allM:
              changed=False
              actualFolder=iterator.ftpName.split("/")
              actualFolder=actualFolder[0:len(actualFolder)-1]
              finalString=""
              for folderName in actualFolder:
                finalString=finalString+folderName+"/"
              actualFolder=finalString[0:len(finalString)-1]
              if actualFolder==directory:
                if iterator.latitude.__str__()!=lat.__str__():
  #                print iterator.latitude.__str__() +" is different from "+lat.__str__()
                  iterator.latitude=lat
                  changed=True
                if iterator.longitude.__str__()!=lon.__str__():
  #                print iterator.longitude.__str__() + " is different from "+lon.__str__()
                  iterator.longitude=lon
                  changed=True
                if changed:
                  iterator.save()
                  print "Saving "+iterator.watermarkName
          except:
            print "Non-existent or improperly formatted GPS Data on "+directory

      else: #it's a folder
        #print "This is a folder: "+f
        traverseGPS(f)



  ftp=FTP()
  ftp.connect(host, port=ftpPort)
  ftp.login(username, password)
  ftpArray=[]
  ftpDict={}
  for j in range(0, maxThreads):
    newFTP=FTP()
    newFTP.connect(host, port=ftpPort)
    newFTP.login(username, password)
    ftpArray.append(newFTP)
    ftpDict[newFTP]=False
  for dir in imageDirectoryFTP:
    if lookForGPS:
      traverseGPS(dir)
    else:
      traverse(dir)
  for ftpObject in ftpArray:
    ftpObject.quit()


imageDirectory='/home/aesg/webapps/boatstatic/uploads/'

pwintyMerchantID="fbdc63de-2e3b-4c57-b8f7-5c6a9f63692c"
pwintyAPIKey="7ac2c133-2274-4e27-a66e-6ba9f1ccdba8"
baseURL="sandbox.pwinty.com" #development
shippingPrice="25.00"
#  baseURL="https://api.pwinty.com" #production

def getPriceDict():
  toRet={}
#  toRet["4x6"]=20.00
#  toRet["5x7"]=30.00
  toRet["dig4x6"]=85.00
  toRet["dig5x7"]=110.00
  toRet["dig8x10"]=110.00
  toRet["8x10"]=125.00
  toRet["11x14"]=200.00

  toRet["16x20"]=250.00
  toRet["20x30"]=400.00
  toRet["24x36"]=550.00
  toRet["36x54"]=800.00
  toRet["44x66"]=900.00
  toRet["canvas"]=1500.00
  toRet["digital"]=500.00

  toRet["50countgreetingcard"]=150.00
  toRet["100countgreetingcard"]=200.00
  toRet["200countgreetingcard"]=300.00
  toRet["400countgreetingcard"]=400.00

  for key, value in toRet.items():
    toRet[key]="%.2f" % value
  return toRet
#"%.2f" % 13.9499999

def createPwintyOrder(addressDictionary):
  import httplib, urllib, simplejson
  destinationURL="/Orders"
  parameterDict={}
  for key, value in addressDictionary.items():
    parameterDict[key]=value

  params = urllib.urlencode(parameterDict)
  headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "X-Pwinty-MerchantId" : pwintyMerchantID, "X-Pwinty-REST-API-Key" : pwintyAPIKey }


  conn = httplib.HTTPSConnection(baseURL+":443")
  conn.request("POST", destinationURL, params, headers)
  response = conn.getresponse() #this is a json response
  #print response.status, response.reason
  data=response.read()
  #response.status 201 means green
  decoded_data=simplejson.loads(data)
  conn.close()

  newOrderId=unicode(decoded_data['id'])
  return newOrderId
  #TODO: error handling here


def addPhotoToPwintyOrder(orderId, pictureDictionary):
  import httplib, urllib, simplejson
  destinationURL="/Photos"
  parameterDict={}
  photoUrl=Map.objects.get(id=int(pictureDictionary['pictureId'])).secretName
  photoUrl="http://boatpix.com/static/uploads/"+photoUrl
  parameterDict['orderId']=orderId
  type=pictureDictionary['size']
  if type=="30x40" or type=="30x45" or type=="40x50":
    type="P"+type
  parameterDict['type']=type

  parameterDict['url']=photoUrl #url of the photo we're printing
  parameterDict['copies']=pictureDictionary['quantity'] #quantity
  parameterDict['sizing']="Crop"
  params = urllib.urlencode(parameterDict)
  headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "X-Pwinty-MerchantId" : pwintyMerchantID, "X-Pwinty-REST-API-Key" : pwintyAPIKey }


  conn = httplib.HTTPSConnection(baseURL+":443")
  conn.request("POST", destinationURL, params, headers)
  response = conn.getresponse() #this is a json response
  #print response.status, response.reason
  data=response.read()
  conn.close()
  return data
def submitPwintyOrder(orderId):
  import httplib, urllib, simplejson
  destinationURL="/Orders/Status"
  parameterDict={}
  parameterDict['id']=orderId
  parameterDict['status']="Submitted"
  params = urllib.urlencode(parameterDict)
  headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "X-Pwinty-MerchantId" : pwintyMerchantID, "X-Pwinty-REST-API-Key" : pwintyAPIKey }
  conn = httplib.HTTPSConnection(baseURL+":443")
  conn.request("POST", destinationURL, params, headers)
  response = conn.getresponse() #this is a json response
  #print response.status, response.reason
  data=response.read()
  conn.close()

  if response.status==201 or response.status==200:
    return True, data
  return False, data


def checkPwintyOrder(orderId):
  import httplib, urllib, simplejson
  destinationURL="/Orders/SubmissionStatus"
  parameterDict={}
  parameterDict['id']=orderId
  params = urllib.urlencode(parameterDict)
  headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "X-Pwinty-MerchantId" : pwintyMerchantID, "X-Pwinty-REST-API-Key" : pwintyAPIKey }
  conn = httplib.HTTPSConnection(baseURL+":443")
  conn.request("GEt", destinationURL, params, headers)
  response = conn.getresponse() #this is a json response
  data=response.read()
  #decoded_data=simplejson.loads(data)
  conn.close()
  return data


#TODO:  add a nice little receipt thingy

def credentials(request):
   login=0
   superuser=0
   if not 'userID' in request.session:
      login=1
   else:
      if request.session['role']=="superuser":
         superuser=1

      currentUser=User.objects.filter(email=request.session['userID'])[0]
   return login, superuser


def generatePassword(password):
   import md5
   password=md5.new(password.__str__()).digest()
   stringAsHex=""
   for character in password:
      stringAsHex=stringAsHex + character.__repr__()
   stringAsHex=stringAsHex.replace("\\x","")
   stringAsHex=stringAsHex.replace("'","")
   stringAsHex=stringAsHex.replace("\"","")
   password=stringAsHex
   return password
def forceLogin(request):
  login, superuser=credentials(request)
  if login:
    return signIn(request)
  return None

def forceSuperUser(request):
  login, superuser=credentials(request)
  if not superuser:
    message="You do not have privileges for this page"
    return render_to_response("success.html", locals())
  return None


def getDistance(zip1, zip2):
  zip1=zip1.__str__()
  zip2=zip2.__str__()
  URL="http://maps.googleapis.com/maps/api/distancematrix/xml?origins="+zip1+"&destinations="+zip2+"&sensor=false"
  import urllib2, urllib
  content=""
  enc_params=urllib.quote(content)
  headers={'Content-Type': 'application/xml'}
  request=urllib2.Request(URL, content, headers)
  r= urllib2.urlopen(request)
  content=r.read()#application/xml, charset=UTF-8

  content=''.join([x.split('>',1)[-1] for x in content.split('<')])
  contentAsArray=content.split()

  #from xml.dom.minidom import parse, parseString
#  dom1=parseString(content)
#  distance=dom1.getElementsByTagName("DistanceMatrixResponse")[0]
  r=""
  index=0
  for iterator in contentAsArray:
    r=r+"["+index.__str__()+"]"+iterator
    index=index+1
  kmDistance=contentAsArray[len(contentAsArray)-2]
  milesDistance=int(float(kmDistance)*0.621371192)
  return milesDistance



def reduce_opacity(im, opacity):
    """Returns an image with reduced opacity."""
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

def watermark(im, mark, position, opacity=1):
    """Adds a watermark to an image."""
    if opacity < 1:
        mark = reduce_opacity(mark, opacity)
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    # create a transparent layer the size of the image and draw the
    # watermark in that layer.
    layer = Image.new('RGBA', im.size, (0,0,0,0))
    if position == 'tile':
        for y in range(0, im.size[1], mark.size[1]):
            for x in range(0, im.size[0], mark.size[0]):
                layer.paste(mark, (x, y))
    elif position == 'scale':
        # scale, but preserve the aspect ratio
        ratio = min(
            float(im.size[0]) / mark.size[0], float(im.size[1]) / mark.size[1])
        w = int(mark.size[0] * ratio)
        h = int(mark.size[1] * ratio)
        mark = mark.resize((w, h))
        layer.paste(mark, ((im.size[0] - w) / 2, (im.size[1] - h) / 2))
    else:
        layer.paste(mark, position)
    # composite the watermark with the layer
    return Image.composite(layer, im, layer)



def get_exif_data(fname):
    ret = {}
    try:
        img = Image.open(fname)
        if hasattr( img, '_getexif' ):
            exifinfo = img._getexif()
            if exifinfo != None:
                for tag, value in exifinfo.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
    except IOError:
        print 'IOERROR ' + fname
    return ret


def gpsInfoToLatLong(gpsInfoFromExif):
  lat = [float(x)/float(y) for x, y in gpsInfoFromExif[2]]
  latref = gpsInfoFromExif[1]
  lon = [float(x)/float(y) for x, y in gpsInfoFromExif[4]]
  lonref = gpsInfoFromExif[3]

  lat = lat[0] + lat[1]/60 + lat[2]/3600
  lon = lon[0] + lon[1]/60 + lon[2]/3600
  if latref == 'S':
    lat = -lat
  if lonref == 'W':
    lon = -lon
  return lat, lon


def dictToString(inDict):
  r=""
  for key, val in inDict.items():
    r=r+key+":   "+val+"\n"
  return r

def handleImage(inImage, originalImageName, mark):
  exifData=get_exif_data_from_image(inImage)
  if not 'DateTimeDigitized' in exifData:
    return#ignore this photo since we can't use it
  dateTaken=exifData['DateTimeDigitized']
  year=dateTaken[0:4]
  month=dateTaken[5:7]
  day=dateTaken[8:10]
  pattern=year+"-"+month+"-"+day+"-"

  directory=imageDirectory
  maxNumber=0

#  relevantMapObjects=Map.objects.filter(watermarkName__contains=pattern)
#  for iterator in relevantMapObjects:
#    if iterator.watermarkName.startswith(pattern):
#      restOfFilename=iterator.watermarkName[len(pattern): len(iterator.watermarkName)].lower()
#      imageNumber=restOfFilename.replace(".jpg","")
#      imageNumber=imageNumber.replace(".jpeg","")
#      if int(imageNumber)>maxNumber:
#        maxNumber=int(imageNumber)
#  for filename in os.listdir(directory):
#    if filename.startswith(pattern):
#      restOfFilename=filename[len(pattern): len(filename)].lower()
#      imageNumber=restOfFilename.replace(".jpg","")
#      imageNumber=imageNumber.replace(".jpeg","")
#      if int(imageNumber)>maxNumber:
#        maxNumber=int(imageNumber)
  newFileMap=Map(watermarkName="will change after save", ftpName=originalImageName)
  newFileMap.dbBoatName=getBoatName(newFileMap.ftpName)
  newFileMap.date=pattern[0:10]
  newFileMap.save()
  newFilename=pattern+str(newFileMap.id)+".jpg"
  newFileMap.watermarkName=newFilename

  currentFolder=originalImageName
  for dir in imageDirectoryFTP:
    currentFolder=currentFolder.replace(dir, "",1)
  currentFolder=currentFolder.replace("\\","/")
  results=currentFolder.split('/')
  results=results[0:len(results)-1]
  finalString=""
  for iterator in results:
    finalString=finalString+iterator+" "
  if len(finalString)>0:
    finalString=finalString[0:len(finalString)-1]
  newFileMap.ftpFolder=finalString
  #print "original location is "+originalImageName
  #print "FTP folder is "+newFileMap.ftpFolder
  if 'GPSInfo' in exifData:
    try:
      gpsData=exifData['GPSInfo']
      lat, lon=gpsInfoToLatLong(gpsData)
      newFileMap.latitude=lat
      newFileMap.longitude=lon
    except: #TODO: handle consistent GPS exif tags
      pass

  try:
    newFileMap.save()
#consider the case where height is greater than width, then you need to use baseHeight
    basewidth=400
    im = inImage
    wpercent=(basewidth/float(im.size[0]))
    hsize=int((float(im.size[1])*float(wpercent)))

    im=im.resize((basewidth, hsize), Image.ANTIALIAS)

    newImage=watermark(im, mark, 'scale', 1.0)


##generate the thumbnail before we add the annoying X
    basewidth=161
    wpercent=(basewidth/float(newImage.size[0]))
    hsize=int((float(newImage.size[1])*float(wpercent)))
    thumbImage=newImage.resize((basewidth, hsize), Image.ANTIALIAS)
    thumbImage.save(directory+"thumbnail-"+newFilename,"jpeg", quality=85)

    transparentLayer=Image.new('RGBA', (newImage.size[0], newImage.size[1]))
    draw=ImageDraw.Draw(transparentLayer)
    draw.line((0, newImage.size[1], newImage.size[0], 0), fill=(255, 255, 255, 120))
    draw.line((0, 0, newImage.size[0], newImage.size[1]), fill=(255,255,255,120))
    newImage.paste(transparentLayer, mask=transparentLayer)
#  newImage=newImage.resize((basewidth, hsize), Image.ANTIALIAS)
    newImage.save(directory+newFilename,"jpeg", quality=85)
    #print newFilename+" saved"
    print ".",


#    newImage=im
  except:
    print "ERROR on image "+originalImageName


greetingCardDirectory="/home/aesg/webapps/boatstatic/greetingcards/"
def buygreetingcards(request, filename):
  title="Greeting Card"
  return render_to_response("buygreetingcards.html", locals())

def greetingcards(request):
  def swap(index1, index2):
    temp=allCards[index1]
    allCards[index1]=allCards[index2]
    allCards[index2]=temp


  title="Select a Greeting Card Template"
  allCards=[]
  for filename in os.listdir(greetingCardDirectory):
    myDict={}
    myDict['filename']=filename
    myDict['number']=int(filename.split(".")[0])
    allCards.append(myDict)
  for j in range(0, len(allCards)-1):
    minIndex=j
    for i in range(j+1, len(allCards)):
      if allCards[i]['number']<allCards[minIndex]['number']:
        minIndex=i
    swap(j, minIndex)

  return render_to_response("greetingcards.html", locals())

def handle_uploaded_files(infile):  #from filename
    directory=imageDirectory
    fname=directory+infile.name
    fname=fname.replace(" ","")
    fname=fname.replace("'","")
    destination=open(fname, 'wb+')
    for chunk in infile.chunks():
      destination.write(chunk)
    destination.close()



    exifData=get_exif_data(fname)
    if not 'DateTimeDigitized' in exifData:
      return#ignore this photo since we can't use it
    dateTaken=exifData['DateTimeDigitized']
    year=dateTaken[0:4]
    month=dateTaken[5:7]
    day=dateTaken[8:10]
    pattern=year+"-"+month+"-"+day+"-"

    maxNumber=0
    for filename in os.listdir(directory):
      if filename.startswith(pattern):
        restOfFilename=filename[len(pattern): len(filename)].lower()
        imageNumber=restOfFilename.replace(".jpg","")
        imageNumber=imageNumber.replace(".jpeg","")
        if int(imageNumber)>maxNumber:
          maxNumber=int(imageNumber)
    newFilename=pattern+str(maxNumber+1)+".jpg"
    randomName=""
    for j in range(0,40):
      var=random.randint(0,25)+65
      randomName=randomName+chr(var)
    randomName=randomName+".jpg"
    newFileMap=Map(watermarkName=newFilename, secretName=randomName)



    if 'GPSInfo' in exifData:
      gpsData=exifData['GPSInfo']
      lat, lon=gpsInfoToLatLong(gpsData)
      newFileMap.latitude=lat
      newFileMap.longitude=lon
    newFileMap.save()

    im = Image.open(fname)
    mark = Image.open(directory+'watermark.png')
    newImage=watermark(im, mark, 'scale', 1.0)
    basewidth=800
    wpercent=(basewidth/float(newImage.size[0]))
    hsize=int((float(newImage.size[1])*float(wpercent)))
    newImage=newImage.resize((basewidth, hsize), Image.ANTIALIAS)
    newImage.save(directory+newFilename,"jpeg")

    newImage=im
    basewidth=161
    wpercent=(basewidth/float(newImage.size[0]))
    hsize=int((float(newImage.size[1])*float(wpercent)))
    newImage=newImage.resize((basewidth, hsize), Image.ANTIALIAS)
    newImage.save(directory+"thumbnail-"+newFilename,"jpeg")

    os.system('mv '+fname+' '+directory+randomName)
#class Map(models.Model):
#  watermarkName=models.CharField(max_length=50)
#  secretName=models.CharField(max_length=50)
#  operator=models.ForeignKey(Operator, null=True)
def adminEdit(request):
  if request.method=="POST":
    directory=imageDirectory
    currentMap=Map.objects.get(id=int(request.POST['id']))
    filename=currentMap.secretName
    try:
      os.system('rm '+ directory+filename)
    except:
      pass
    filename=currentMap.watermarkName
    try:
      os.system('rm '+ filename)
    except:
      pass
      currentMap.delete()
  allM=Map.objects.all()
  allImages=[]
  for iterator in allM:
    filename="thumbnail-"+iterator.watermarkName
    dictionary={}
    dictionary['src']=filename
    dictionary['id']=iterator.id
    allImages.append(dictionary)

  return render_to_response("adminedit.html", locals())
def listUpload(request):
    # Handle file upload
    if request.method == 'POST':
      for afile in request.FILES.getlist('filesToUpload'):
        handle_uploaded_files(afile)
      return HttpResponse("worked")
            # Redirect to the document list after POST
    else:
      pass
    # Load documents for the list page
#    documents = Document.objects.all()
    documents=0

    # Render list page with the documents and the form
    return render_to_response(
        'list.html', locals())

def ftpSelectionSort(inList):
  def swap(index1, index2):
    temp=inList[index1]
    inList[index1]=inList[index2]
    inList[index2]=temp

  for j in range(0, len(inList)-1):
    minIndex=j
    for i in range(j+1, len(inList)):
      if inList[i][0]>inList[minIndex][0]:
        minIndex=i
    swap(j, minIndex)
  return inList

def selectionSort(inList,criteria):
  def swap(index1, index2):
    temp=inList[index1]
    inList[index1]=inList[index2]
    inList[index2]=temp

  for j in range(0, len(inList)-1):
    minIndex=j
    for i in range(j+1, len(inList)):
      if criteria=='name' and inList[i].name.lower()<inList[minIndex].name.lower():
        minIndex=i
      if criteria=='relevancy' and inList[i].relevancy>inList[minIndex].relevancy:
        minIndex=i
      if criteria=='number' and inList[i].number<inList[minIndex].number:
        minIndex=i
      if criteria=='intrinsic' and inList[i]<inList[minIndex]:
        minIndex=i
      if criteria=='date' and inList[i].date>inList[minIndex].date:
        minIndex=i
    swap(j, minIndex)
  return inList
import re
def getBoatNumber(fullPath):
  allWords=fullPath.replace("\\","/").split("/")
  ret=allWords[len(allWords)-1]
  ret=ret.replace(".jpg","")
  ret=ret.replace(".JPG","")
  ret=ret.replace("_",".")
  firstSplit=ret.split(".")
  number=firstSplit[len(firstSplit)-1]
  if isNumber(number):
    return number
  return ""

def getBoatName(fullPath, lower=True):
  allWords=fullPath.replace("\\","/").split("/")
  ret=allWords[len(allWords)-1]
  ret=ret.replace(".jpg","")
  ret=ret.replace(".JPG","")
  ret=ret.replace("_",".")
  firstSplit=ret.split(".")
  firstStringIsRegistration=True
  if re.match("^[A-Za-z]*$", firstSplit[0].replace(" ","")):
    firstStringIsRegistration=False
  numKeywords=2
  if not firstStringIsRegistration:
    numKeywords=1
  if len(firstSplit)>numKeywords:
    firstSplit=firstSplit[0:numKeywords]

  if isNumber(firstSplit[len(firstSplit)-1]):
    firstSplit=firstSplit[0:len(firstSplit)-1]
  ret=""
  for iterator in firstSplit:
    ret=ret+iterator+" "
  ret=ret.replace("_"," ")
  if lower:
    return ret.lower()
  else:
    return ret


def adminOld(request):
#this data structure is a dictionary of dictionaries.  Top Dict is based on exercise name
  yearDict={}

#optimization answered quite nicely at http://stackoverflow.com/questions/5636482/django-optimizing-many-to-many-query
  allOrders=list(Order.objects.select_related('readyToShip').all())
  initialQuery=None
#  orderMap={}
#  for orderObject in allOrders:
#    orderMap[orderObject.id]=orderObject
#    orderObject.pictureList=[]
#
#  for pictureObject in ReadyToShip.pictures.through.select_related('picture').filter(readyToShip_id__in=???):
#    orderMap[pictureObject.readyToShip_id].pictureList.append(pictureObject.picture)



  for iterator in allOrders:
    querySetObject=iterator.readyToShip.pictures.select_related('map').all()
    iterator.readyToShip.pictureList=list(querySetObject)
    currentDate=iterator.datetime.date()
    dateKey=currentDate.year.__str__()+", "+(currentDate.month-1).__str__()+", "+currentDate.day.__str__()
    if not currentDate.year.__str__() in yearDict:
      yearDict[currentDate.year.__str__()]=collections.OrderedDict()
    if not dateKey in yearDict[currentDate.year.__str__()]:
      yearDict[currentDate.year.__str__()][dateKey]=0
    yearDict[currentDate.year.__str__()][dateKey]=yearDict[currentDate.year.__str__()][dateKey]+iterator.total

#    if initialQuery==None:
#      initialQuery=querySetObject
#    else:
#      initialQuery=initialQuery | querySetObject
#  allPictureObjects=list(initialQuery)


  #relevantWorkoutSeries=WorkoutSeries.objects.select_related().filter(todaysWorkout__in=userWorkouts)
  #allExercises=todaysWorkout.exercises.select_related('exercise','exercise__workoutComponent').all()
  return render_to_response("admin.html", locals())

def emailAdmin(request):
  if 'isAuthenticatedAdmin' in request.session and request.session['isAuthenticatedAdmin']:
    ftpObject=FTP()
    ftpObject.connect(host, port=ftpPort)
    ftpObject.login(username, password)

    email=EmailMessage()
    email.subject="Digital Copy of Selected Photo"
    email.body=""
    email.body=email.body+"The attached image has just been grabbed and emailed to this address\n"
    emailTo=[request.POST['email']]
#  emailTo=["scott.lobdell@gmail.com"]
    email.to=emailTo
    mapObject=Map.objects.get(id=int(request.POST['pictureId']))
    image=fetchPictureFromMapObject(mapObject, ftpObject)
    localFile=StringIO()
    image.save(localFile, format="jpeg")
    imageData=localFile.getvalue()
    localFile.close()
    email.attach("Digital Print.jpg", imageData, "image/jpeg")
    email.send()
    ftpObject.quit()
    return HttpResponseRedirect("/")
    return render_to_response("blank.html", locals())
  data="You are not a logged in administrator!"
  return render_to_response("blank.html", locals())

def mustAuthenticate(request):
  if request.method=="POST":
    if request.POST['password']=="pictureboat1$":
      request.session['isAuthenticatedAdmin']=True
      request.session.modified = True  #force save
      return HttpResponseRedirect("../admin")
  return render_to_response("mustauthenticate.html", locals())


def admin(request):
  if not 'isAuthenticatedAdmin' in request.session or request.session['isAuthenticatedAdmin']!=True:
    return HttpResponseRedirect("../mustauthenticate")
  title="Control Panel"
  from datetime import datetime
  from datetime import timedelta
  import locale
  locale.setlocale(locale.LC_ALL, 'en_CA.UTF-8')
  now=datetime.now()
  yesterday=now-timedelta(days=1)
  currentYear=now.year
  currentMonth=now.month
  yearStart=datetime(year=int(currentYear), month=1, day=1)
  monthStart=datetime(year=int(currentYear), month=now.month, day=1)
  ordersThisYear=Order.objects.filter(datetime__range=(yearStart,now)).select_related('readyToShip')
  ordersThisMonth=Order.objects.filter(datetime__range=(monthStart, now)).select_related('readyToShip')
  boatQueries=BoatQuery.objects.filter(datetime__range=(yesterday, now))

  for iterator in boatQueries:
    iterator.found=False
    keywords=iterator.text.lower().split(" ")
    testQuery=Map.objects.all()
    for inner in keywords:
      testQuery=testQuery.filter(dbBoatName__icontains=inner)
    if testQuery.count()>0:
      iterator.found=True

  yearTotal=0
  monthTotal=0
  yearOrders=0
  monthOrders=0
  for iterator in ordersThisYear:
    yearTotal=yearTotal+iterator.total
    yearOrders+=1
  for iterator in ordersThisMonth:
    monthTotal=monthTotal+iterator.total
    monthOrders+=1
  monthAverage=0
  yearAverage=0
  if monthOrders>0:
    monthAverage=locale.currency(monthTotal/monthOrders, grouping=True)
  if yearOrders>0:
    yearAverage=locale.currency(yearTotal/yearOrders,grouping=True)
  monthTotal=locale.currency(monthTotal, grouping=True)
  yearTotal=locale.currency(yearTotal, grouping=True)
  pattern=currentYear.__str__()+"-"
  boatsThisYear=Map.objects.filter(watermarkName__contains=pattern).values_list('dbBoatName', flat=True).distinct()
  #boatsThisYear=selectionSort(boatsThisYear, 'name')
  numberBoatsThisYear=boatsThisYear.count()

  boatsThatHaveBeenOrdered=[]
  sizeDict={}
  totalPictures=0

  dictOfPictureLists={}#key will be workout ID
  readyToShipObjects=[]
  for iterator in ordersThisYear:
    readyToShipObjects.append(iterator.readyToShip)
  relevantReadyToShip_Pictures=ReadyToShip_Pictures.objects.select_related().filter(readytoship__in=readyToShipObjects)
  for iterator in relevantReadyToShip_Pictures:
    key=iterator.readytoship.id
    if not key in dictOfPictureLists:
      dictOfPictureLists[key]=[]
    dictOfPictureLists[key].append(iterator.picture)
    if iterator.picture.size in sizeDict:
      sizeDict[iterator.picture.size]+=1
    else:
      sizeDict[iterator.picture.size]=1
      myMap=iterator.picture.map
      boatName=getBoatName(iterator.picture.map.ftpName, False)
      if not boatName in boatsThatHaveBeenOrdered:
        boatsThatHaveBeenOrdered.append(boatName)
    #dictOfSeriesLists[key].append(iterator.series)
  totalPictures=0
  for key, value in dictOfPictureLists.items():
    totalPictures+=len(value)
#  for key, value

#  for iterator in ordersThisYear:
#    pictureList=list(iterator.readyToShip.pictures.select_related('map').all())
###FIX THIS
#    for iterator in pictureList:
#      totalPictures+=1
#      if iterator.size in sizeDict:
#        sizeDict[iterator.size]+=1
#      else:
#        sizeDict[iterator.size]=1
#      myMap=iterator.map
#      boatName=getBoatName(iterator.map.ftpName, False)
#      if not boatName in boatsThatHaveBeenOrdered:
#        boatsThatHaveBeenOrdered.append(boatName)
  conversionRate=0
  if not len(boatsThisYear)==0:
    conversionRate=round(100.0*(float(len(boatsThatHaveBeenOrdered))/len(boatsThisYear)),2)
  for key, value in sizeDict.items():
    sizeDict[key]=round(100.0*(float(value)/totalPictures),2)
  picsThisYear=Map.objects.filter(watermarkName__contains=currentYear.__str__()+"-").count()
  picsTotal=Map.objects.count()
  end=datetime.now()
  start=end-timedelta(days=7)

  if request.method=="POST":
    from django.core import serializers
    startArray=request.POST['start'].split("/")
    endArray=request.POST['end'].split("/")
    startMonth=int(startArray[0])
    startDay=int(startArray[1])
    startYear=int(startArray[2])
    endMonth=int(endArray[0])
    endDay=int(endArray[1])
    endYear=int(endArray[2])
    start=datetime(month=startMonth, day=startDay, year=startYear)
    end=datetime(month=endMonth, day=endDay, year=endYear, hour=23, minute=59, second=59)
    allRequests=PhotoRequest.objects.filter(dateOfRequest__range=(start, end))
    data=serializers.serialize("python", allRequests)
  return render_to_response("admin.html", locals())



def resultsAsCSV(request, sMonth, sDay, sYear, eMonth, eDay, eYear):
  response=HttpResponse(mimetype="text/csv")
  response['Content-Disposition'] = 'attachment; filename="Speculation Orders.csv"'
  from datetime import datetime
  import csv
  startMonth=int(sMonth)
  startDay=int(sDay)
  startYear=int(sYear)
  endMonth=int(eMonth)
  endDay=int(eDay)
  endYear=int(eYear)
  start=datetime(month=startMonth, day=startDay, year=startYear)
  end=datetime(month=endMonth, day=endDay, year=endYear, hour=23, minute=59, second=59)


  allRequests=PhotoRequest.objects.filter(dateOfRequest__range=(start, end))
  writer = csv.writer(response)
  writer.writerow(['Date of Request','Customer Name','Registration Type', 'USCG Document Number', 'Date of Photo', 'Boat Name','Photo Location','Hailing Port','Boat Make','Boat Length', 'State Registration', 'Sail Number','Day Phone','ext', 'Evening Phone','ext','Cell Phone','Fax','Email','Address','City','State','Zip Code','Country','Comments'])
  for iterator in list(allRequests):
    if iterator.comments==None:
      iterator.comments=""
    writer.writerow([iterator.dateOfRequest,  iterator.customerName,  iterator.registrationType,  iterator.uscgDocumentNumber,  iterator.dateOfPhoto,  iterator.boatName,  iterator.photoLocation,  iterator.hailingPort,  iterator.boatMake,  iterator.boatLength,  iterator.stateRegistration,  iterator.sailNumber,  iterator.dayPhone,  iterator.ext,  iterator.eveningPhone,  iterator.ext,  iterator.cellPhone,  iterator.fax,  iterator.email,  iterator.address+" "+iterator.city+", "+iterator.state+"    "+iterator.zipCode,  iterator.city,  iterator.state,  iterator.zipCode,  iterator.country,  iterator.comments.replace("\n"," ")])
  return response

def greetingCardsAsCSV(request, sMonth, sDay, sYear, eMonth, eDay, eYear):
  response=HttpResponse(mimetype="text/csv")
  response['Content-Disposition'] = 'attachment; filename="Greeting Card Orders.csv"'
  from datetime import datetime
  import csv
  startMonth=int(sMonth)
  startDay=int(sDay)
  startYear=int(sYear)
  endMonth=int(eMonth)
  endDay=int(eDay)
  endYear=int(eYear)
  start=datetime(month=startMonth, day=startDay, year=startYear)
  end=datetime(month=endMonth, day=endDay, year=endYear, hour=23, minute=59, second=59)
  allOrders=GreetingCardOrder.objects.filter(datetime__range=(start, end))
  writer=csv.writer(response)

  writer.writerow(['Picture','Size','Line 1','Line 2','Line 3','Price','Quantity','Boat Name','Sail Number','Boat Make', 'Length','Year','First Name','Last Name','Day Phone','Evening Phone','Email Address','Address','Total','Card Type', 'Card Last 4','CVV2','Exp Month', 'Exp Year', 'Special Instructions'])
  for iterator in allOrders:
    if iterator.comments==None:
      iterator.comments=""
    extraOrderInfo=iterator.order
    writer.writerow([iterator.picture, iterator.size, iterator.line1, iterator.line2, iterator.line3, iterator.price, iterator.quantity, iterator.boatName, iterator.sailNumber, iterator.boatMake, iterator.length, iterator.year, iterator.firstName, iterator.lastName, iterator.dayPhone, iterator.eveningPhone, iterator.emailAddress, extraOrderInfo.address.replace("\n","     "), extraOrderInfo.total, extraOrderInfo.cardType, extraOrderInfo.lastFour, extraOrderInfo.cv2, extraOrderInfo.expMonth, extraOrderInfo.expYear, iterator.comments.replace("\n"," ")])
  return response

def ordersAsCSV(request, sMonth, sDay, sYear, eMonth, eDay, eYear):
  response=HttpResponse(mimetype="text/csv")
  response['Content-Disposition'] = 'attachment; filename="Online Image Orders.csv"'
  from datetime import datetime
  import csv
  startMonth=int(sMonth)
  startDay=int(sDay)
  startYear=int(sYear)
  endMonth=int(eMonth)
  endDay=int(eDay)
  endYear=int(eYear)
  start=datetime(month=startMonth, day=startDay, year=startYear)
  end=datetime(month=endMonth, day=endDay, year=endYear, hour=23, minute=59, second=59)
  allOrders=Order.objects.select_related('readyToShip').filter(datetime__range=(start, end))
  writer=csv.writer(response)
  writer.writerow(['Order ID','Name','Email','Address','Total','Datetime','Size','Quantity','Matte / Gloss', 'File', 'Card Type','Card Last 4','CVV2','Exp Month','Exp Year'])
  for iterator in allOrders:
    readyToShipObject=iterator.readyToShip
    allPics=readyToShipObject.pictures.select_related().all()
    for inner in allPics:
      writer.writerow([iterator.id.__str__(), iterator.name, readyToShipObject.email, iterator.address.replace("\n","     "), iterator.total, iterator.datetime, inner.size, inner.quantity, inner.matteGloss, inner.map.ftpName, iterator.cardType, iterator.lastFour, iterator.cv2, iterator.expMonth, iterator.expYear])
  return response

def getBoatListFromSearch(keywords, inList, exactMatch=False):
  results=[]
  for iterator in inList:
    iterator.boatName=getBoatName(iterator.ftpName)
    iterator.relevancy=0.0
    added=False
    for inner in keywords:
      if inner in iterator.boatName:
        if not added:
          boatNameLength=len(iterator.boatName.replace(" ",""))
          if boatNameLength!=0:
            iterator.relevancy=iterator.relevancy+float(len(inner))/boatNameLength
          else:
            iterator.relevancy=.8#total guess right here
          if exactMatch and iterator.relevancy<0.99:
            pass
          else:
            results.append(iterator)
            added=True
  allMap=selectionSort(list(results), 'relevancy')
  return allMap

def searchBoat(request):
  title="Search for your boat by vessel name or registration number"
  searchType="Search for a Boat"
  finalString=""
  allM=Map.objects.all()
  resultsPerPage=12
  pageNumber=1
  if "results" in request.GET:
    resultsPerPage=int(request.GET['results'])
  if "page" in request.GET:
    pageNumber=int(request.GET["page"])

  if 'boat' in request.GET:
    originalBoat=request.GET["boat"]
    if originalBoat=="":
      return render_to_response("searchboat.html")
    trackingData=BoatQuery(text=originalBoat)
    trackingData.datetime=datetime.datetime.now()
    x_forwarded_for=request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
      trackingData.ip=x_forwarded_for.split(',')[0]
    else:
      trackingData.ip=request.META.get('REMOTE_ADDR', '<none>')
    trackingData.save()
    keywords=(request.GET['boat'].lower()).split(" ")
    finalQuery=None
    allM=Map.objects.all()
    if "event" in request.GET and request.GET["event"]!="":
      allM=allM.filter(ftpFolder=request.GET["event"])
    for iterator in keywords:
      allM=allM.filter(dbBoatName__icontains=iterator)

#    for iterator in keywords:
#      allM=Map.objects.filter(ftpName__icontains=iterator)
#
#      if finalQuery==None:
#        finalQuery=allM
#      else:
#        finalQuery=finalQuery | allM
    allM=list(allM)
    allMap=getBoatListFromSearch(keywords, allM)
    allMap=groupBoatsByEvent(allMap)
    for iterator in allMap:
      #iterator.boatName=getBoatName(iterator.ftpName, False)
      iterator.boatName=iterator.dbBoatName+" "+getBoatNumber(iterator.ftpName)
    totalResults=len(allMap)
    allMap, indices, prev, next=resultsByPage(allMap, resultsPerPage, pageNumber)
  return render_to_response('searchboat.html', locals())


def searchEvent(request):
  title="Search for your boat based on the associated event it participated in"
  searchType="Search by Event"
  finalString=""
  if 'event' in request.GET:
    allM=Map.objects.all()
    keywords=(request.GET['event'].lower()).split(" ")
    for iterator in keywords:
      allM=allM.filter(ftpFolder__icontains=iterator)
    allEvents=list(allM.values_list('ftpFolder', flat=True).distinct())

#    results=[]
#    for iterator in allM:
#      iterator.eventName=iterator.ftpFolder.lower().replace("\\"," ").replace("/"," ")
#      iterator.relevancy=0.0
#      added=False
#      for inner in keywords:
#        if inner in iterator.ftpFolder:
#          if not added:
#            results.append(iterator)
#            added=True
#          iterator.relevancy=iterator.relevancy+float(len(inner))/len(iterator.ftpFolder)
#    toRemove=[]
#    allMap=selectionSort(list(results), 'relevancy')
#    allEvents=[]
    totalResults=len(allEvents)
  else:
    allExistingEvents=getAllEvents()
    #allExistingEvents=selectionSort(allExistingEvents, "name")
  return render_to_response('searchevent.html', locals())

def getLatestEvent(inList):
  eventName=""
  randomMapObject=None
  import datetime
  import calendar
  maxDate=None
  for iterator in inList:
    if iterator.ftpFolder=="":
      pass
    else:
      dateString=iterator.watermarkName.replace(".jpg","")
      year=dateString[0:4]
      month=dateString[5:7]
      day=dateString[8:10]
      now=datetime.datetime(year=int(year), month=int(month), day=int(day))
      if maxDate==None or now>maxDate:
        maxDate=now
        eventName=iterator.ftpFolder.replace("\\"," ").replace("/"," ")
        randomMapObject=iterator


  return eventName, randomMapObject
def getRandomEventExcept(latestMapObject, inList):
  if latestMapObject==None:
    return None, None
  from random import shuffle
  eventName=""
  randomMapObject=None
  copyList=[]
  for iterator in inList:
    if iterator.ftpFolder!="" and iterator.ftpFolder!=latestMapObject.ftpFolder:
      copyList.append(iterator)
  shuffle(copyList)
  try:
    eventName=copyList[0].ftpFolder.replace("\\"," ").replace("/"," ")
    randomMapObject=copyList[0]
    return eventName, randomMapObject
  except:
    return None, None

def demo(request):
  allM=list(Map.objects.all())
  from random import shuffle
  shuffle(allM)
  myList=[]
  counter=0
  for iterator in allM:
    if counter<14:
      myList.append(iterator)
    counter+=1
  allM=myList
  return render_to_response("demo.html", locals())

def getAllEvents():
  allEvents=list(Map.objects.values_list('ftpFolder', flat=True).distinct())
  return allEvents

  allM=Map.objects.all()
  import datetime
  import calendar
  allEvents=[]
  reverseEventDict={}
  for iterator in allM:
    iterator.eventName=iterator.ftpFolder.replace("\\"," ").replace("/"," ")
    iterator.name=iterator.eventName
    dateString=iterator.watermarkName.replace(".jpg","")
    year=dateString[0:4]
    month=dateString[5:7]
    day=dateString[8:10]
    now=datetime.datetime(year=int(year), month=int(month), day=int(day))
    iterator.date=now
    iterator.named_month = calendar.month_name[int(month)]
    if not iterator.eventName in allEvents and iterator.eventName!="":
      allEvents.append(iterator.eventName)
      reverseEventDict[iterator.eventName]=iterator
  allEvents=[]
  for key, value in reverseEventDict.items():
    allEvents.append(value)
  return allEvents

def events(request):
  tab=1
  title="Boatpix Events"
  sortByName=False
  if request.method=="POST":
    if request.POST["sortBy"]=="name":
      sortByName=True


  allEvents=getAllEvents()
  allEvents.sort()
#  if sortByName:
#    allEvents=selectionSort(allEvents, "name")
#  else:
#    allEvents=selectionSort(allEvents, "date")
  return render_to_response("events.html",locals())

def splitImage(inImage, filename, numberOfTiles=10, offSet=False):
  filename="temp-"+filename.__str__()
  img=inImage
  width, height=img.size
  numTiles=numberOfTiles
  tileWidth=width/numTiles
  tileHeight=height/numTiles
  tiles=[]
  mark = Image.open(imageDirectory+'watermark.png')
  negOne=0
  offsetCol=0
  offsetRow=0
  if offSet:
    negOne=1
    offsetCol=tileWidth/2
    offsetRow=tileHeight/2
  for row in range (0,numTiles-negOne):
    for col in range (0,numTiles-negOne):
      box=(col*tileWidth, row*tileHeight, col*tileWidth+tileWidth+offsetCol, row*tileHeight+tileHeight+offsetRow)
      tempImage=img.crop(box)
      tempImage=watermark(tempImage, mark, 'scale', 0.4)
      tempFilename=filename+row.__str__()+col.__str__()+".jpg"
      if offSet:
        tempFilename="offset-"+tempFilename
      tempImage.save("/home/aesg/webapps/boatstatic/uploads/"+tempFilename, format="jpeg")
#      tempImage.save(output, format="jpeg")
      tiles.append(tempFilename)
  return tiles

def shrinkImage(inPhoto, targetWidth, targetHeight):
  currentWidth=inPhoto.size[0]
  currentHeight=inPhoto.size[1]
  #assume that photo is landscape
  if currentHeight>currentWidth:
    temp=targetWidth
    targetWidth=targetHeight
    targetHeight=temp
  heightRatio=float(targetHeight)/currentHeight
  widthRatio=float(targetWidth)/currentWidth  #in theory these should be equal but probably wont
  if heightRatio>widthRatio:
    #we want to shrink based on the ratio of height
    targetWidth=currentWidth*heightRatio
  elif widthRatio>heightRatio:
    targetHeight=currentHeight*widthRatio
  im=inPhoto
  im=im.resize((targetWidth, targetHeight), Image.ANTIALIAS)
  return im

def getOriginalImage(request):
  if not "pictureId" in request.GET:
    return HttpResponse("")
  pictureId=int(request.GET['pictureId'])
  mapObject=Map.objects.get(id=pictureId)
  ftpObject=FTP()
  ftpObject.connect(host, port=ftpPort)
  ftpObject.login(username, password)
  image=fetchPictureFromMapObject(mapObject, ftpObject)
  ftpObject.quit()
  filename="superWatermark.png"
  mark=Image.open(imageDirectory+filename)
  image=watermark(image, mark, 'tile', 0.3)

  randomName=""
  for j in range(0,50):
    var=random.randint(0,25)+65
    randomName=randomName+chr(var)
  randomName=randomName+".jpg"
  image.save("/home/aesg/webapps/boatstatic/previews/"+randomName, "JPEG")
  return HttpResponse(randomName)

def fullImage(request):
  if not "pictureId" in request.GET:
    return HttpResponse("")
  pictureId=request.GET["pictureId"]
  return render_to_response("fullimage.html",locals())


def beforeAfter(request):

  return render_to_response("beforeafter.html",locals())
def home(request):
  #isLoggedIn, currentUser, isFree=credentials(request)
  import datetime
  from random import shuffle
  now=datetime.datetime.now()
  currentYear=now.year
  difference=currentYear-1995
  directory=imageDirectory
  slideList=[]
  maxSize=10
  counter=0
#  latestObject=Map.objects.all().order_by('-watermarkName')[:1]
#  latestObject=list(latestObject)
  currentCache=CustomCache.objects.select_related("latestMap", "randomMap").all()[0]


#  maxDate=Map.objects.all().aggregate(Max("date"))
#  latestMapObject=Map.objects.filter(date=maxDate["date__max"])[0]
  latestMapObject=currentCache.latestMap
  allEvents=[]
  if currentCache.eventNames!="":
    allEvents=currentCache.eventNames.split("|")
#  try:
#  xxxx
#  eventName, latestMapObject=getLatestEvent(allM)
#    latestMapObject=latestObject[0]
  eventName=latestMapObject.ftpFolder.replace("\\"," ").replace("/"," ")
#  except:
#    pass
#  totalSize=Map.objects.count()

  #allM=list(Map.objects.all().order_by('?')[:maxSize+1])
  #randomMapObject=allM[maxSize]
  randomMapObject=currentCache.randomMap#Map.objects.all()[random.randint(0, totalSize)]
  eventName2=randomMapObject.ftpFolder.replace("\\"," ").replace("/"," ")
  #eventName2, randomMapObject=getRandomEventExcept(latestMapObject, allM)
  #shuffle(allM)
  #for iterator in list(allM):
  #  if counter<maxSize:
      #iterator.eventName=iterator.ftpFolder.replace("\\"," ").replace("/"," ")
      #if iterator.eventName=="":
      #  iterator.eventName="BoatPix"
  #    slideList.append(iterator)
  #  counter=counter+1
  allM=slideList
  goodPics=os.listdir("/home/aesg/webapps/boatstatic/base/goodpics")
  slideList=goodPics
  shuffle(slideList)
  tempArray=[]
  for j in range(0, maxSize):
    if j<len(slideList):
      tempArray.append(slideList[j])
  slideList=tempArray
#  if isLoggedIn:
  #return render_to_response("home.html", locals())
  #return HttpResponse(getDistance(77479, 76549))
  year=now.year
  month=now.month
  #if latestObject:
    #latestObject=latestObject[0]
  dateString=latestMapObject.watermarkName
  year=dateString[0:4]
  month=dateString[5:7]
  return render_to_response("home.html", locals())

def getDistance(mapObject1, mapObject2):
    p1=mapObject1
    p2=mapObject2
    lat1=p1.latitude
    lon1=p1.longitude
    lat2=p2.latitude
    lon2=p2.longitude
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

def getPictureCluster():
  allMaps=list(Map.objects.filter(latitude__isnull=False))
  listDict={}
  acceptableDistance=6 #KM
  for j in range(0, len(allMaps)):
    #first find out if it's in the same location as an existing pic
    currentPicture=allMaps[j]
    found=False
    for k in range(0, len(allMaps)):
      if j==k:
        pass
      else:
        compareToPicture=allMaps[k]

        if getDistance(currentPicture, compareToPicture)<acceptableDistance:
          print getDistance(currentPicture, compareToPicture)
          if compareToPicture in listDict:
            listToUse=listDict[compareToPicture]
          else:
            listToUse=[]
            listToUse.append(compareToPicture)
            listDict[compareToPicture]=listToUse
          listToUse.append(currentPicture)
          listDict[currentPicture]=listToUse
          found=True
          break
    if not found:
      listToUse=[]
      listToUse.append(currentPicture)
      listDict[currentPicture]=listToUse
  matrix=[]
  for key, pictureArray in listDict.items():
    if not pictureArray in matrix:
      matrix.append(pictureArray)
  return matrix

def getLatLongDict():
#returns a dictionary based on lat long coordinates
  allMaps=list(Map.objects.filter(latitude__isnull=False))
  returnDict={}
  for iterator in allMaps:
    key=(iterator.latitude, iterator.longitude)
    if not key in returnDict:
      returnDict[key]=[]
    returnDict[key].append(iterator)
  latestItemDict={}
  for key, value in returnDict.items():
    latestObject=Map.objects.filter(latitude=key[0], longitude=key[1]).order_by('-watermarkName')[:1]
    latestItemDict[key]=latestObject[0]
  return returnDict, latestItemDict

def getUniqueLocationMapObjects():
  latLongs=Map.objects.values_list('latitude','longitude').distinct()
  allQueries=None
  from itertools import chain
  for coordinates in latLongs:
    if coordinates[0]!=None:
      query=Map.objects.filter(latitude=coordinates[0], longitude=coordinates[1]).order_by('watermarkName')[:1]
      if allQueries==None:
        allQueries=query
      else:
        allQueries=chain(allQueries, query)
  allMaps=list(allQueries)
  return allMaps

def map(request):
  title="Find Your Photos Using a Map"
  def getAspectRatio(fname):
    img = Image.open(imageDirectory+fname)
    size=img.size
    width=size[0]
    height=size[1]
    aspectRatio=float(width)/height
    return aspectRatio
  #matrix=getPictureCluster()
  finalArray=[]
#  latLongDict, latestItemDict=getLatLongDict()
#all we really need
  uniqueLocationMapObjects=getUniqueLocationMapObjects()
  for iterator in uniqueLocationMapObjects:
    randomPicture=iterator.watermarkName
    mapId=iterator.id
    maxDateString=iterator.watermarkName
    year=maxDateString[0:4]
    month=maxDateString[5:7]
    dict={}
    dict['latitude']=iterator.latitude
    dict['longitude']=iterator.longitude
    dict['picture']=randomPicture
    dict['id']=mapId
    dict['aspectRatio']=getAspectRatio(randomPicture)
    dict['maxMonth']=month.__str__()
    dict['maxYear']=year.__str__()
    finalArray.append(dict)

#  for key, arrayObject in latLongDict.items():
#    randomIndex=random.randint(0, len(arrayObject)-1)
#    randomPicture=arrayObject[randomIndex].watermarkName
#    mapId=arrayObject[randomIndex].id
#    maxDateString=latestItemDict[key].watermarkName
#    year=maxDateString[0:4]
#    month=maxDateString[5:7]
#    dict={}
#    dict['latitude']=key[0]
#    dict['longitude']=key[1]
#    dict['picture']=randomPicture
#    dict['id']=mapId
#    dict['aspectRatio']=getAspectRatio(randomPicture)
#    dict['maxMonth']=month.__str__()
#    dict['maxYear']=year.__str__()
#    finalArray.append(dict)

#  import datetime
#  import calendar
#  for arrayObject in matrix:
#    randomIndex=random.randint(0,len(arrayObject)-1)
#    randomPicture=arrayObject[randomIndex].watermarkName
#    mapId=arrayObject[randomIndex].id
#    averageLat=0
#    averageLon=0
#    maxDate=None

#    for iterator in arrayObject:
#      averageLat=averageLat+iterator.latitude
#      averageLon=averageLon+iterator.longitude
#      dateString=iterator.watermarkName.replace(".jpg","")
#      year=dateString[0:4]
#      month=dateString[5:7]
#      day=dateString[8:10]
#      now=datetime.datetime(year=int(year), month=int(month), day=int(day))
#      if maxDate==None or now>maxDate:
#        maxDate=now
#
#    averageLat=averageLat/len(arrayObject)
#    averageLon=averageLon/len(arrayObject)
#    dict={}
#    dict['latitude']=averageLat
#    dict['longitude']=averageLon
#    dict['picture']=randomPicture
#    dict['id']=mapId
#    dict['aspectRatio']=getAspectRatio(randomPicture)
#    dict['maxMonth']=maxDate.month.__str__()
#    dict['maxYear']=maxDate.year.__str__()
#    finalArray.append(dict)
  #now we need a list of colocated items
  return render_to_response("map.html", locals())

def isNumber(inString):
  try:
    int(inString)
    return True
  except:
    return False
def addtocartdigital(request):
  tab=7
  title="Cart"
  backUrl="/"
  if 'back' in request.session:
    backUrl=request.session['back']
  if request.method=="POST":
    for key, value in request.POST.items():
      if "picture_" in key:
        pictureId=int(key.replace("picture_",""))
        if 'cart' in request.session:
          pass
        else:
          request.session['cart']=[]
        itemDict={}
        itemDict['pictureId']=pictureId
        itemDict['size']="digital"
        itemDict['quantity']=1
        itemDict['matteGloss']="N/A"
        request.session['cart'].append(itemDict)
    request.session.modified = True  #force save
    currentCart=[]
    for iterator in request.session['cart']:
      iterator["map"]=Map.objects.get(id=int(iterator['pictureId']))
      currentCart.append(iterator)
#best process would be to find all the boats with the same name and set the rules there
    currentCart=adjustPricesByBoat(currentCart)
  return render_to_response("addtocart.html", locals())

def adjustPricesByBoat(inCart):
#cart is a dictionary full of items
  initialPrices=getPriceDict()
  allDigitalBoats=[]
  uniqueOccurences=[]
  sixteenByTwentyCount=0
  for iterator in inCart:
    if iterator["size"]=="digital":
      currentBoat=getBoatName(Map.objects.get(id=int(iterator['pictureId'])).ftpName)
      allDigitalBoats.append(currentBoat)
      if not currentBoat in uniqueOccurences:
        uniqueOccurences.append(currentBoat)
    elif iterator["size"]=="16x20":
      sixteenByTwentyCount+=int(iterator["quantity"])
    if iterator["matteGloss"]=="canvas":
      iterator["price"]=round(float(initialPrices[iterator["size"]])*3.5,2)
  boatDict={}
  threeFreeSixteenByTwenties=False
  for iterator in uniqueOccurences:
    numOccurences=allDigitalBoats.count(iterator)
    price=float(getPriceDict()["digital"])
    if numOccurences==1:
      pass
    elif numOccurences==2:
      price=125.00
    elif numOccurences>=3:
      price=150.00
      threeFreeSixteenByTwenties=True
    price=price/numOccurences
    price=round(price, 2)
    boatDict[iterator]=price
  for key, value in boatDict.items():
    for iterator in inCart:
      currentBoat=getBoatName(Map.objects.get(id=int(iterator['pictureId'])).ftpName)
      if currentBoat==key and iterator["size"]=="digital":
        iterator["price"]=value

  if threeFreeSixteenByTwenties:
    sixteenByTwentyCount-=3
  if sixteenByTwentyCount>1:
    newPrice=0
    if sixteenByTwentyCount==2:
      newPrice=400.0/2
    elif sixteenByTwentyCount>=3:
      newPrice=500.0/3
    for iterator in inCart:
      if iterator['size']=='16x20':
        iterator['price']=newPrice
  if threeFreeSixteenByTwenties:
    counter=0
    for iterator in inCart:
      if iterator['size']=='16x20' and counter<3:
        counter+=1
        iterator['price']=0

  return inCart

def getFilenameFilter(fullPath):
  filenameFilter=fullPath.replace("\\","/").split("/")
  filenameFilter=filenameFilter[len(filenameFilter)-1]
  firstSplit=filenameFilter.split(".")
  firstStringIsRegistration=True
  if re.match("^[A-Za-z]*$", firstSplit[0].replace(" ","")):
    firstStringIsRegistration=False
  numKeywords=2
  if not firstStringIsRegistration:
     numKeywords=1
  if len(firstSplit)>numKeywords:
    firstSplit=firstSplit[0:numKeywords]
  if isNumber(firstSplit[len(firstSplit)-1]):
    firstSplit=firstSplit[0:len(firstSplit)-1]
  filenameFilter=""
  for iterator in firstSplit:
    filenameFilter=filenameFilter+iterator+"."
  return filenameFilter

def addgreetingcardtocart(request):
  def copyPostValToDict(inDict,key):
    inDict[key]=request.POST[key]
    return inDict
  def appendtocart(value, quantity):
    itemDict={}
    itemDict['picture']=request.POST['picture']
    itemDict['quantity']=quantity
    itemDict['size']=value.__str__()+"countgreetingcard"
    itemDict['prettysize']=value.__str__()+" Count Greeting Card"
    itemDict['line1']=request.POST['line1']
    itemDict['line2']=request.POST['line2']
    itemDict['line3']=request.POST['line3']
    prices=getPriceDict()
    itemDict['price']=prices[itemDict['size']]
    itemDict=copyPostValToDict(itemDict, 'boatName')
    itemDict=copyPostValToDict(itemDict, 'sailNumber')
    itemDict=copyPostValToDict(itemDict, 'boatMake')
    itemDict=copyPostValToDict(itemDict, 'length')
    itemDict=copyPostValToDict(itemDict, 'year')
    itemDict=copyPostValToDict(itemDict, 'firstName')
    itemDict=copyPostValToDict(itemDict, 'lastName')
    itemDict=copyPostValToDict(itemDict, 'dayPhone')
    itemDict=copyPostValToDict(itemDict, 'eveningPhone')
    itemDict=copyPostValToDict(itemDict, 'emailAddress')
    itemDict=copyPostValToDict(itemDict, 'comments')
    request.session['greetingcards'].append(itemDict)
  def isInt(value):
    try:
      junk=int(value)
      return True
    except:
      return False
  title="Cart"
  tab=7
  backUrl="/"
  if 'back' in request.session:
    backUrl=request.session['back']
  if not 'greetingcards' in request.session:
    request.session['greetingcards']=[]
  if request.method=="POST":
    for iterator in request.POST:
      if 'quantity' in iterator and isInt(request.POST[iterator]):
        if iterator.startswith('50'):
          appendtocart(50, request.POST[iterator])
        elif iterator.startswith('100'):
          appendtocart(100, request.POST[iterator])
        elif iterator.startswith('200'):
          appendtocart(200, request.POST[iterator])
        elif iterator.startswith('400'):
          appendtocart(400, request.POST[iterator])
    request.session.modified = True  #force save
  if 'cart' in request.session:
    cartList=request.session['cart']
    for iterator in cartList:
      iterator['pictureUrl']="thumbnail-"+Map.objects.get(id=iterator['pictureId']).watermarkName
  else:
    cartList=[]
  return render_to_response("cart.html", locals())

def addtocart(request):
  title="Cart"
  tab=7
  from random import shuffle
  backUrl="/"
  if 'back' in request.session:
    backUrl=request.session['back']
  if request.method=="GET":
    quantity=request.GET['quantity']
    size=request.GET['size']
    pictureId=request.GET['pictureid']
    if not "dig" in size:
      matteGloss=request.GET['matteGloss']
    else:
      matteGloss="N/A"
    if 'cart' in request.session:
      pass# already exists
    else:
      request.session['cart']=[]
    itemDict={}
    itemDict['pictureId']=pictureId
    itemDict['size']=size
    itemDict['quantity']=quantity
    itemDict['matteGloss']=matteGloss

    #check if there's already this item in the session
    nothingExistsAlready=True
    for iterator in request.session['cart']:
      if int(iterator['pictureId'])==int(pictureId) and iterator['size']==size and iterator['matteGloss']==matteGloss:
        iterator['quantity']=int(iterator['quantity'])+int(quantity)
        nothingExistsAlready=False
    if nothingExistsAlready:
      request.session['cart'].append(itemDict)

    request.session.modified = True  #force save
    currentCart=[]
    for iterator in request.session['cart']:
      currentCart.append(iterator)
    allM=Map.objects.all()
    debugString=""
    otherBoats=[]
    for iterator in currentCart:
      iterator["map"]=Map.objects.get(id=int(iterator['pictureId']))
      currentBoat=(iterator["map"].ftpName.lower()).split("/")
      currentBoat=currentBoat[len(currentBoat)-1].replace(".jpg","")
      keywords=currentBoat.split(".")
      if isNumber(keywords[len(keywords)-1]):
        keywords=keywords[0:len(keywords)-1]
      currentBoat=""
      for item in keywords:
        currentBoat=currentBoat+item+" "
      currentBoat=currentBoat.replace("."," ")
      keywords=currentBoat.split(" ")



      filenameFilter=getFilenameFilter(iterator['map'].ftpName)
      allM=list(Map.objects.filter(ftpName__contains=filenameFilter)[:50])
      toAdd=getBoatListFromSearch(keywords, allM)#list of maps
      moreBoats=[]
      for inner in toAdd:
	if not inner in otherBoats and not inner in moreBoats:
	  moreBoats.append(inner)
      toRemove=[]
      for inner in moreBoats:
        if inner==iterator["map"]:
          toRemove.append(inner)
	elif inner.relevancy<0.5:
	  toRemove.append(inner)

      for inner in toRemove:
        moreBoats.remove(inner)
      otherBoats.extend(moreBoats)

    shuffle(otherBoats)
    if len(otherBoats)>6:
      otherBoats=otherBoats[0:6]
  cartList=request.session['cart']
  prices=getPriceDict()
  for iterator in cartList:
    iterator['price']=prices[iterator['size']]
  request.session['cart']=adjustPricesByBoat(request.session['cart'])
  return render_to_response("addtocart.html", locals())




def basicsearch(request):
  import datetime
  from django.core.mail import send_mail
  send_mail("Someone Redirected", "junk", 'administrator@oraclefitness.com', ["scott.lobdell@gmail.com"], fail_silently=False)
  return HttpResponseRedirect("http://boatpix.com")
  title="We'll find your boat for you!"
  if request.method=="POST":
    basicEmail(request.POST)
    message="Request received!  We'll get back to you shortly"
    import datetime
    newRequest=PhotoRequest()
    newRequest.dateOfRequest=datetime.datetime.now()
    newRequest.customerName=request.POST['firstName']+" "+request.POST['lastName']
    newRequest.registrationType=request.POST['lRegistrationType']
    #newRequest.uscgDocumentNumber=models.CharField(max_length=30, null=True)
    newRequest.dateOfPhoto=datetime.date(month=int(request.POST['month']), year=int(request.POST['year']), day=int(request.POST['day']))
    newRequest.boatName=request.POST['vesselName']
    newRequest.photoLocation=request.POST['photoLocation']
    newRequest.hailingPort=request.POST['hailingPort']
    newRequest.boatMake=request.POST['boatMake']
    try:
      newRequest.boatLength=int(request.POST['length'])
    except:
      newRequest.boatLength=0
    newRequest.stateRegistration=request.POST['stateRegistration']
    newRequest.sailNumber=request.POST['sailNumber']
    newRequest.dayPhone=request.POST['dayPhone']
    #newRequest.ext=xxxx
    newRequest.eveningPhone=request.POST['eveningPhone']
    #newRequest.ext=xxx
    newRequest.cellPhone=request.POST['cellPhone']
    newRequest.fax=request.POST['fax']
    newRequest.email=request.POST['email']
    newRequest.address=request.POST['streetAddress']
    newRequest.city=request.POST['city']
    newRequest.state=request.POST['state']
    newRequest.zipCode=request.POST['zipCode']
    newRequest.country=request.POST['country']
    newRequest.comments=request.POST['comments']
    newRequest.save()

    return render_to_response("success.html", locals())
  return render_to_response("basicsearch.html", locals())

def facialRecognition(request):
  title="Search for your pictures by uploading a picture of your face"
  return render_to_response("facialrecognition.html", locals())
def requestEvent(request):
  tab=2
  title="Request Aerial Photography Services for Your Event"
  if request.method=="POST":
    if request.POST["secAnswer"]!="" and int(request.POST["secAnswer"])==request.session["sum"]:
      basicEmail(request.POST)
      message="Request received!  We'll get back to you shortly"
      return render_to_response("success.html", locals())
    else:
      message="You don't look human to us"
      return render_to_response("success.html", locals())
  var1=random.randint(0, 10)
  var2=random.randint(0,10)
  request.session["sum"]=var1+var2
  request.session.modified = True  #force save
  return render_to_response("request.html", locals())


def pricing(request):
  tab=3
  title="Pricing Details"
  return render_to_response("pricing.html", locals())

#precondiction is that this is already sorted, and "boatName" exists
def groupBoatsByEvent(inList):
  ret=[]
  previousString="this could be anything"
  for iterator in inList:
    if iterator.ftpFolder!=previousString:
      ret.append(iterator)
      previousString=iterator.ftpFolder
  return ret

def eliminateDuplicateBoatNames(inList):
  ret=[]
  previousString="this could be anything"
  for iterator in inList:
    if iterator.boatName.lower()!=previousString.lower():
      ret.append(iterator)
      previousString=iterator.boatName
  return ret

def event(request):
  showMultiplePicsOfSameBoat=False
  if 'showMultiplePicsOfSameBoat' in request.GET and request.GET['showMultiplePicsOfSameBoat'].lower()=="true":
    showMultiplePicsOfSameBoat=True
  if "event" in request.GET:
    title=request.GET['event']
  else:
    return HttpResponseRedirect("../")
  allM=list(Map.objects.filter(ftpFolder=title))
  if not allM:
    allM=list(Map.objects.filter(ftpFolder__icontains=title))
  #return HttpResponse(Map.objects.filter(ftpFolder=title).count().__str__())
  toUse=[]
  for mapObject in allM:
    filenameToUse=mapObject.watermarkName
    myNum=int(filenameToUse[11:len(filenameToUse)].replace(".jpg",""))
    mapObject.number=myNum
    mapObject.boatName=getBoatName(mapObject.ftpName, False)
    mapObject.name=mapObject.boatName
  #  if mapObject.ftpFolder.replace("\\"," ").replace("/"," ")==title:
    toUse.append(mapObject)
  allM=toUse
  allM=selectionSort(allM, 'name')

  if not showMultiplePicsOfSameBoat:
    allM=eliminateDuplicateBoatNames(allM)

  resultsPerPage=12
  pageNumber=1
  if "results" in request.GET:
    resultsPerPage=int(request.GET['results'])
  if "page" in request.GET:
    pageNumber=int(request.GET["page"])
  allM, indices, prev, next=resultsByPage(allM, resultsPerPage, pageNumber)
  facebookUrl="http://boatpixxx.com/event/?event="+title
  return render_to_response("event.html", locals())

def faq(request):
  tab=4
  title="Frequently Asked Questions"
  return render_to_response("faq.html", locals())


def viewphoto(request, filename):
#date and event name
  currentObject=Map.objects.filter(watermarkName=filename)
  if currentObject:
    currentObject=currentObject[0]
  else:
    from django.http import Http404
    raise Http404
  dateString=currentObject.watermarkName.replace(".jpg","")
  year=dateString[0:4]
  month=dateString[5:7]
  day=dateString[8:10]
  now=datetime.datetime(year=int(year), month=int(month), day=int(day))
  import calendar
  named_month = calendar.month_name[int(month)]
  #title =day+" "+named_month+" "+year+", "+currentObject.ftpFolder
  title=currentObject.ftpFolder
    #return 404
  otherBoats=[]
#  boatName=getBoatName(currentObject.ftpName, False)
  boatName=currentObject.dbBoatName
  otherBoats=list(Map.objects.filter(dbBoatName=boatName)[:3])
#  filenameFilter=getFilenameFilter(currentObject.ftpName)
#  otherBoatQuery=list(Map.objects.filter(ftpName__contains=filenameFilter))
  #otherBoatQuery=Map.objects.all()#filter(ftpName__contains=boatName)
#  debugString=boatName
#  for iterator in otherBoatQuery:
#    iterator.boatName=getBoatName(iterator.ftpName)
#    if iterator.boatName==boatName.lower():
#      otherBoats.append(iterator)


  if len(otherBoats)>3:
    otherBoats=otherBoats[0:3]
#  return HttpResponse(debugString)
  pictureId=(currentObject).id
  pattern=filename[0:10]
  possibleFiles=[]
  currentNumber=filename[11:len(filename)].replace(".jpg","")
  currentNumber=int(currentNumber)
  allM=Map.objects.filter(date=pattern).order_by('dbBoatName')
#  for iterator in possibleFiles:
#  myString=""
#  for iterator in allM:
#    myString+=iterator.dbBoatName+"<br/>"
  #return HttpResponse(myString)
  originalSearchQuery=None
  originalEventName=None

  if "boat" in request.GET:
    originalSearchQuery=request.GET["boat"]
    keywords=(originalSearchQuery.lower()).split(" ")
    for iterator in keywords:
      allM=allM.filter(dbBoatName__icontains=iterator)
    allM=list(allM)
    results=getBoatListFromSearch(keywords, allM)
  eventList=[]
  if "event" in request.GET:
    originalEventName=request.GET['event']
    allM=allM.filter(ftpFolder=originalEventName)

  allM=list(allM)
  try:
    currentIndex=allM.index(currentObject)
  except:
    from django.http import Http404
    raise Http404
  nextIndex=currentIndex+1
  prevIndex=currentIndex-1
  if prevIndex<0:
    prevIndex=len(allM)-1
  if nextIndex>=len(allM):
    nextIndex=0
  prevFileName=allM[prevIndex].watermarkName
  nextFileName=allM[nextIndex].watermarkName

  #this loop was used

#    newList.append(iterator.watermarkName)
#  possibleFiles=newList
#  numbers=[]
#  for aFile in possibleFiles:
#    myNumber=int(aFile[11:len(aFile)].replace(".jpg",""))
#    numbers.append(myNumber)
#  minNext=99999
#  minPrevious=-9999
#  nextNumber=0
#  prevNumber=0
#  for iterator in numbers:
   # find the closest negative and closest posive
#    result=iterator-currentNumber
#    if result>0:#this is for NEXT
#      if result<minNext:
#        minNext=result
#        nextNumber=iterator
#    elif result<0:#this is for PREVIOUS
#      if result > minPrevious:
#        minPrevious=result
#        prevNumber=iterator

#  if nextNumber==0:
#    nextFilename=""
#  else:
#    nextNumber=nextNumber.__str__()
#    nextFileName=pattern+"-"+nextNumber+".jpg"
#
#  if prevNumber==0:
#    prevFilename=""
#  else:
#    prevNumber=prevNumber.__str__()
#    prevFileName=pattern+"-"+prevNumber+".jpg"
#
  prices=getPriceDict()
  for key, value in prices.items():
    prices[key]=int(float(value))
  return render_to_response("viewphoto.html", locals())

def customize(request):
  pictureId=request.GET['pictureId']
  mapObject=Map.objects.get(id=int(pictureId))
  prices=getPriceDict()
  for key, value in prices.items():
    prices[key]=int(float(value))
  return render_to_response("customize.html", locals())

def multiplePrintsWizard(request):
  title="Order Multiple Digital Prints at a Discounted Rate"
  currentMapObject=Map.objects.get(id=int(request.GET["pictureid"]))
  currentBoatName=getBoatName(currentMapObject.ftpName)
  keywords=currentBoatName.lower().split(" ")
  #allM=list(Map.objects.filter(yyyy))
  filenameFilter=getFilenameFilter(currentMapObject.ftpName)
  allM=list(Map.objects.filter(ftpName__contains=filenameFilter))
  possibleBoats=getBoatListFromSearch(keywords, allM)
  matchedBoats=[]

  for iterator in possibleBoats:
    if getBoatName(iterator.ftpName)==currentBoatName:
      matchedBoats.append(iterator)

  return render_to_response("wizard.html", locals())

def resultsByPage(inArray, resultsPerPage, currentPage):
###################
  numberPages=float(len(inArray)/float(resultsPerPage))  #need to get the ceiling of this
  numberPages=int(math.ceil(numberPages))
  pageNumber=int(currentPage)
  if pageNumber>numberPages:
    pageNumber=numberPages
  startNumber=(pageNumber-1)*resultsPerPage+1 #NUMBER, not INDEX.  i.e. 1st is index 1
  endNumber=startNumber-1+resultsPerPage
  counter=1
  toDisplay=[]
  for iterator in inArray:
    if counter >= startNumber and counter <=endNumber:
      #add to ToDisplay
      toDisplay.append(iterator)
    counter=counter+1
  indices=[]
  for j in range (1, numberPages+1):
    indices.append(j)
  next=pageNumber+1
  prev=pageNumber-1
  if prev<1:
    prev=numberPages
  if next>numberPages:
    next=1
  return toDisplay, indices, prev, next
###################


def exactmatch(request):
  boatName="None"
  ftpFolder=None
  if "boat" in request.GET:
    boatName=request.GET["boat"]
  if "event" in request.GET:
    ftpFolder=request.GET["event"]
  title="All Photos of "+boatName

#less than ideal right here
  firstKeyword=boatName.replace("%20"," ").split(" ")[0]
  #allM=Map.objects.filter(dbBoatName__contains=firstKeyword)
  allM=Map.objects.filter(dbBoatName=boatName)
  if allM==None:
    allM=Map.objects.filter(dbBoatName__icontains=boatName)
  if ftpFolder!=None:
    allM=allM.filter(ftpFolder=ftpFolder)
  resultsPerPage=200
  pageNumber=1
  if "results" in request.GET:
    resultsPerPage=int(request.GET['results'])
  if "page" in request.GET:
    pageNumber=int(request.GET["page"])

  if 'boat' in request.GET:
    originalBoat=request.GET["boat"]
    keywords=(request.GET['boat'].lower()).split(" ")
    allMap=getBoatListFromSearch(keywords, allM, True)
    for iterator in allMap:
      iterator.boatName=iterator.dbBoatName+" "+getBoatNumber(iterator.ftpName)
#getBoatName(iterator.ftpName, False)
    totalResults=len(allMap)
    allMap, indices, prev, next=resultsByPage(allMap, resultsPerPage, pageNumber)


  return render_to_response("exactmatch.html", locals())


def viewphotos(request, month, day, year, existingId=None):
  matrix=None
  arrayToUse=None
  showMultiplePicsOfSameBoat=False
  if(int(month)<10):
    month="0"+str(month)
  if(int(day)<10):
    day="0"+str(day)
  pattern=str(year)+"-"+str(month)+"-"+str(day)
  allM=None
  if 'showMultiplePicsOfSameBoat' in request.GET and request.GET['showMultiplePicsOfSameBoat'].lower()=="true":
    showMultiplePicsOfSameBoat=True
  if existingId!=None:
    #matrix=getPictureCluster()
    #for arrayObject in matrix:
    #  for iterator in arrayObject:
    #    if int(iterator.id)==int(existingId):
    #      arrayToUse=arrayObject
    #      break
    currentObject=Map.objects.get(id=existingId)
#    latLongDict, latestItemDict=getLatLongDict()
#    arrayToUse=latLongDict[(currentObject.latitude, currentObject.longitude)]
    pattern=year.__str__()
    allM=list(Map.objects.filter(latitude=currentObject.latitude, longitude=currentObject.longitude, watermarkName__contains=pattern))
  else:
    allM=list(Map.objects.filter(watermarkName__contains=pattern))



  if 'HTTP_REFERRER' in request.META:
    request.session['back']=request.META['HTTP_REFERRER']
  currentUrl=request.META.get('PATH_INFO')
  request.session['back']=currentUrl
  directory=imageDirectory


  imageList=[]
#  allM=Map.objects.all()
  for iterator in allM:
    #if pattern in iterator.watermarkName:
    iterator.boatName=getBoatName(iterator.ftpName, False)
    iterator.name=iterator.boatName
    if existingId!=None and arrayToUse:
      if iterator in arrayToUse:
        filenameToUse=iterator.watermarkName
        myNum=int(filenameToUse[11:len(filenameToUse)].replace(".jpg",""))
        iterator.number=myNum
        imageList.append(iterator)
    else:
      filenameToUse=iterator.watermarkName
      myNum=int(filenameToUse[11:len(filenameToUse)].replace(".jpg",""))
      iterator.number=myNum
      imageList.append(iterator)
  imageList=selectionSort(imageList, 'name')
  if not showMultiplePicsOfSameBoat:
    imageList=eliminateDuplicateBoatNames(imageList)
#  toUse=[]
#  for iterator in imageList:
#    toUse.append(iterator.watermarkName)
#  imageList=toUse


  resultsPerPage=12
  pageNumber=1
  if "results" in request.GET:
    resultsPerPage=int(request.GET['results'])
  if "page" in request.GET:
    pageNumber=int(request.GET["page"])
  imageList, indices, prev, next=resultsByPage(imageList, resultsPerPage, pageNumber)



  import calendar
  named_month = calendar.month_name[int(month)]
  title="View Photos from "+day.__str__()+" "+named_month+" "+year.__str__()
  month=month.replace("0","")
  day=day.replace("0","")
  facebookUrl="http://boatpixxx.com/viewphotos"+month.__str__()+"-"+day.__str__()+"-"+year.__str__()
  return render_to_response("viewphotos.html", locals())

# SBL this is what I need to use
def findphotos(request, month, year, existingId=None):
  title="Calendar"

  import calendar
  #allOrders=GreetingCardOrder.objects.filter(datetime__range=(startDateTime, endDateTime))
  now=datetime.datetime(year=int(year), month=int(month), day=1)
  endOfMonth=datetime.datetime(year=int(year), month=int(month), day=calendar.mdays[now.month])
  named_month = calendar.month_name[int(month)]
  prevy=nexty=int(year)
  prevm=int(month)-1
  if prevm==0:
    prevm=12
    prevy=prevy-1
  nextm=int(month)+1
  if nextm==13:
    nextm=1
    nexty=nexty+1
  day=now.isoweekday()
  if day==7:
    day=0
  logDictionary={}
#  for iterator in relevantLogs:
#    key=iterator.date.day.__str__()
#    if key in logDictionary:
#      logDictionary[key].append(iterator)
#    else:
#      logDictionary[key]=[]
#      logDictionary[key].append(iterator)

  dayMatrix=[]
  aWeek=[]
  for j in range(0, day):
    dictionary={}
    dictionary['day']=""
    aWeek.append(dictionary)


  for j in range(1, calendar.mdays[now.month]+1):
    dictionary={}
    dictionary['day']=j
    if j.__str__() in logDictionary:
      dictionary['entries']=logDictionary[j.__str__()]
    aWeek.append(dictionary)
    if len(aWeek)==7:
      dayMatrix.append(aWeek)
      aWeek=[]
  dayMatrix.append(aWeek)


  allM=None
  pictureDictionary={}
  directory=imageDirectory
  pattern=year+"-"
  month=int(month)
  if int(month)<10:
    pattern=pattern+"0"
  pattern=pattern+str(month)+"-"
  matrix=None
  arrayToUse=None
  from itertools import chain
  currentObject=None
  if existingId!=None:
    currentObject=Map.objects.get(id=existingId)


  #allOrders=GreetingCardOrder.objects.filter(datetime__range=(startDateTime, endDateTime))
  #now=datetime.datetime(year=int(year), month=int(month), day=1)
  #endOfMonth=datetime.datetime(year=int(year), month=int(month), day=calendar.mdays[now.month]+1)
  allDates=Map.objects.filter(date__range=(now, endOfMonth))
  if existingId!=None:
    allDates=Map.objects.filter(date__range=(now, endOfMonth), latitude=currentObject.latitude, longitude=currentObject.longitude)
  #allM=allM.order_by('date').distinct('date')#
  allDates=allDates.values_list('date', flat=True).distinct()
  allQueries=None
  for dateObject in allDates:
    query=Map.objects.filter(date=dateObject)[:1]
    if allQueries==None:
      allQueries=query
    else:
      allQueries=chain(allQueries, query)
  allM=[]
  if allQueries!=None:
    allM=list(allQueries)

  if False:
    allQueries=None
    for day in range(1,32):
      dayString=""
      if day<10:
        dayString="0"+day.__str__()
      else:
        dayString=day.__str__()
      newPattern=pattern+dayString

      if existingId!=None:
        query=Map.objects.filter(latitude=currentObject.latitude, longitude=currentObject.longitude, watermarkName__contains=newPattern)[:1]
      else:
        query=Map.objects.filter(watermarkName__contains=newPattern)[:1]
      if allQueries==None:
        allQueries=query
      else:
        allQueries=chain(allQueries, query)
    allM=list(allQueries)
    #latLongDict, latestItemDict=getLatLongDict()
    #arrayToUse=latLongDict[(currentObject.latitude, currentObject.longitude)]

    #matrix=getPictureCluster()
    #for arrayObject in matrix:
    #  for iterator in arrayObject:
    #    if int(iterator.id)==int(existingId):
    #      arrayToUse=arrayObject
    #      break


  #if allM==None:
  #  allM=Map.objects.filter(watermarkName__contains=pattern)

  for iterator in allM:
    currentDay=int((iterator.watermarkName.replace(pattern,""))[0:2]  )
    pictureDictionary[currentDay]="thumbnail-"+iterator.watermarkName
#  for filename in os.listdir(directory):
#    if pattern in filename:
#      currentDay=(filename.replace(pattern,""))[0:2]
#      currentDay=int(currentDay)
#      if existingId!=None and arrayToUse:
#        for mapObject in arrayToUse:
#          if "thumbnail-"+mapObject.watermarkName==filename:
#            pictureDictionary[currentDay]=filename
#        #filename must be in the arrayToUse
#      else:
#        pictureDictionary[currentDay]=filename

  return render_to_response("calendar.html", locals())


def dictToString(inDict):
  retString=""
  for key, value in inDict.items():
    retString=retString+key+":    "+value.replace("%20"," ")+"<br/>\n"
  return retString

def emailPicture(pictureObj, emailTo, ftpObj):
  ftp=ftpObj
  email=EmailMessage()
  email.subject="Digital Print Delivery!"
  email.body="Thanks for your order!  Attached you'll find the image you ordered from Boatpix.com."
  email.from_email="Boat Pix <no-reply@boatpix.com>"
  email.to=[emailTo]
  photoMap=pictureObj.map


  randomName=""
  for j in range(0,40):
    var=random.randint(0,25)+65
    randomName=randomName+chr(var)
  randomName=randomName+".jpg"

  image=fetchPictureFromMapObject(pictureObj.map, ftp)
  newSize=None
  if pictureObj.size=="dig4x6":
    newSize=(600, 900)
  elif pictureObj.size=="dig5x7":
    newSize=(750, 1050)
  elif pictureObj.size=="dig8x10":
    newSize=(1200, 1500)
  if newSize:
    image=shrinkImage(image, newSize[1], newSize[0])
#def shrinkImage(inPhoto, targetWidth, targetHeight):
  image.save(imageDirectory+randomName,"jpeg")
  email.attach_file(imageDirectory+randomName)
#  email.attach('image.jpg', list(imageData.getdata()), "image.jpg")
  email.send()
  os.system('rm '+ imageDirectory+randomName)


def ipn(request):
  message=""

  import os, sys

  try:
    if request.method=='POST':
      pwintyOrderNumber=request.POST['item_number']
      readyToShip=ReadyToShip.objects.filter(orderNumber=int(pwintyOrderNumber))[0]
      allPictures=readyToShip.pictures.select_related('map').all()
      allDigitalOrder=True
      for iterator in allPictures:
        if iterator.size!="digital":
          allDigitalOrder=False
      success=True
      if not allDigitalOrder:
        success, message=submitPwintyOrder(pwintyOrderNumber)
      #success=True
      import datetime
      from django.core.mail import send_mail
      if success:
        completedOrder=Order()
        completedOrder.orderNumber=int(pwintyOrderNumber)
        completedOrder.name=request.POST['first_name']+" "+request.POST['last_name']
        completedOrder.address=request.POST['address_street']+"\n"+request.POST['address_city']+"\n"+"\n"+request.POST['address_zip']
        completedOrder.total=request.POST['mc_gross']
        completedOrder.datetime=datetime.datetime.now()
        completedOrder.readyToShip=readyToShip
        completedOrder.save()
###
 	#DID NOT GET THIS WORKING
        #allPictures=list(readyToShip.pictures.all())
        for iterator in allPictures:
          if iterator.size=="digital" or "30" in iterator.size or "40" in iterator.size:
            #pass
            emailPicture(iterator, readyToShip.email)
            #email this pic
##
        send_mail("Order Completed", pwintyOrderNumber, 'administrator@oraclefitness.com', ["scott.lobdell@gmail.com"], fail_silently=False)
      else:
        error=checkPwintyOrder(pwintyOrderNumber)

        send_mail("Order Failed", pwintyOrderNumber+"\n"+error, 'administrator@oraclefitness.com', ["scott.lobdell@gmail.com"], fail_silently=False)
  except Exception, e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    message=(exc_type, fname, exc_tb.tb_lineno)


    from django.core.mail import send_mail
    send_mail("COMPLETE FAILd", message, 'administrator@oraclefitness.com', ["scott.lobdell@gmail.com"], fail_silently=False)

  return HttpResponse("worked")


#last_name:    Smith<br/>
#txn_id:    59891330<br/>
#receiver_email:    seller@paypalsandbox.com<br/>
#payment_status:    Completed<br/>
#tax:    2.02<br/>
#residence_country:    US<br/>
#address_state:    CA<br/>
#payer_status:    verified<br/>
#txn_type:    web_accept<br/>
#address_street:    123, any street<br/>
#payment_date:    06:30:59 Aug 09, 2012 PDT<br/>
##first_name:    John<br/>
#item_name:    something<br/>
#address_country:    United States<br/>
#charset:    windows-1252<br/>
#custom:    xyz123<br/>
#notify_version:    2.1<br/>
#address_name:    John Smith<br/>
#mc_gross_1:    9.34<br/>
#test_ipn:    1<br/>
#item_number:    AK-1234<br/>
#receiver_id:    TESTSELLERID1<br/>
#business:    seller@paypalsandbox.com<br/>
#payer_id:    TESTBUYERID01<br/>
#verify_sign:    A07w9HD-lFrpKd.fq-XRn4bRXsoXATnDNJGq4NeiaTMstLZIu8vwinz3<br/>
#address_zip:    95131<br/>
#address_country_code:    US<br/>
#address_city:    San Jose<br/>
#address_status:    confirmed<br/>
##mc_fee:    0.44<br/>
#mc_currency:    USD<br/>
#shipping:    3.04<br/>
#payer_email:    buyer@paypalsandbox.com<br/>
#payment_type:    instant<br/>
#mc_gross:    12.34<br/>
#quantity:    1<br/>



def shippingandbilling(request):
  return HttpResponse("")
def orderreview(request):
  return HttpResponse("")
def ordercomplete(request):
  return HttpResponse("")


def doPayPalAction(postDict):
#DEVELOPMENT
  username="test_1344301619_biz_api1.pictureblimp.com"
  password="R8CDR7EYFMBYZLML"
  signature="ATBky8GcIX1ehiAaONqaLidR9wp-A.x82yBVoNRU55p3..QgxFbJIclx"
  merchantEmailAddress="test_1344301619_biz@pictureblimp.com"
  baseURL="api-3t.sandbox.paypal.com"

#PRODUCTIOn

  #username="scott_api1.pictureblimp.com"
  #password="LACA5BNMQWBZMMSA"
  #signature="Ay5.XEP337fGmUerBItDojfZ2sljA5VdvCkYp28oAypZYN295pdF8hjM"
  #merchantEmailAddress="scott@pictureblimp.com"
  #baseURL="api-3t.paypal.com"
  destinationURL="/nvp"
  postDict['USER']=username
  postDict['PWD']=password
  postDict['SIGNATURE']=signature
  import httplib, urllib, simplejson
  params = urllib.urlencode(postDict)
  headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
  conn = httplib.HTTPSConnection(baseURL+":443")
  conn.request("POST", destinationURL, params, headers)
  response = conn.getresponse() #this is a json response
  #print response.status, response.reason
  data=response.read()
  dataArray=data.split("&")
  responseDict={}
  for iterator in dataArray:
    twoValues=iterator.split("=")
    key=twoValues[0]
    value=twoValues[1]
    responseDict[key]=value
    #response.status 201 means green
  conn.close()
  return responseDict


#START
#API Credentials
#ensure this is passed as x.xx


def startPayPalTransaction(dollarAmount):
  postDict={}
  postDict['METHOD']="SetExpressCheckout"
  postDict['PAYMENTREQUEST_0_AMT']=dollarAmount
  postDict['PAYMENTREQUEST_0_SHIPPINGAMT']=shippingPrice#TODO: do some arithmatic for floats and stuff
  postDict['PAYMENTREQUEST_0_ITEMAMT']="5.05"
  postDict['RETURNURL']="http://pictureblimp.com/finalizeorder"
  postDict['CANCELURL']="http://pictureblimp.com/cart"
  #postDict['CALLBACK']="http://pictureblimp.com/ipn"
  postDict['NOSHIPPING']="0"
  postDict['ADDROVERRIDE']="0"
  postDict['VERSION']="92.0"
  postDict['SOLUTIONTYPE']="Sole"
  #encode the parameters
  #POST the data to the NVPSandBoxServer
  #read the response
  responseDict=doPayPalAction(postDict)
  return dictToString(responseDict)
  if responseDict['ACK']=="Success":
    return responseDict['TOKEN']
  else:
   return False

def getExpressCheckoutDetails(token):
  postDict={}
  postDict['METHOD']="GetExpressCheckoutDetails"
  postDict['TOKEN']=token
  responseDict=doPayPalAction(postDict)
  return responseDict['PAYERID']

def doExpressCheckoutPayment(token, payerid, amount):
  postDict={}
  postDict['PAYMENTREQUEST_0_PAYMENTACTION']="Sale"
  postDict['TOKEN']=token
  postDict['PAYERID']=payerid
  postDict['PAYMENTREQUEST_0_AMT']=amount
  responseDict=doPayPalAction(postDict)


def startpaypalorder(request):
  from django.http import HttpResponseRedirect
  amount="10.00"#amout must be formatted like this...calculate this stuff from the session
  failOrToken=startPayPalTransaction(amount)
  if not failOrToken:
    #we failed
    return HttpResponse("error starting paypal transaction")
  token=failOrToken
  request.session['amount']=amount
  request.session['token']=token
  request.session.modified = True  #force save
  #DEV
  return HttpResponseRedirect("https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token="+token)
  #Production
  return HttpResponseRedirect("https://www.paypal.com/webscr?cmd=_express-checkout&token="+token)

#<form action="https://www.paypal.com/cgi-bin/webscr" method="post">
#<input type="hidden" name="cmd" value="_xclick">
#    <input type="hidden" name="business" value="paypal@mmi-hamburg.com">
# <input type="hidden" name="business" value="business login?">
# <input type="hidden" name="item_name" value="hat">
# <input type="hidden" name="item_number" value="123">
# <input type="hidden" name="amount" value="15.00">
# <input type="hidden" name="first_name" value="John">
# <input type="hidden" name="last_name" value="Doe">
# <input type="hidden" name="address1" value="any Street">
# <input type="hidden" name="address2" value="Apt 5">
# <input type="hidden" name="city" value="any town">
# <input type="hidden" name="state" value="CA">
# <input type="hidden" name="zip" value="00000">
# <input type="hidden" name="night_phone_a" value="610">
# <input type="hidden" name="night_phone_b" value="555">
# <input type="hidden" name="night_phone_c" value="1234">
# <input type="hidden" name="email" value="name@mail.com">


#<input type="submit" name="submit" alt="Make payments with PayPal - it's fast, free and secure!">
#</form>




#return HttpResponseRedirect("https://www.paypal.com/webscr?cmd=_express-checkout&token="+token)

def finalizeorder(request):
  amount=request.session['amount']
  token=request.session['token']
 # payerid=getExpressCheckoutDetails(token)
 # doExpressCheckoutPayment(token, payerid, amount)
  return render_to_response("finalizeorder.html", locals())




#user returns to site

#use API for GetExpressCheckoutDetails
#this only requires the checkout token

#DoExpressCheckoutPayment
#this requires PAYMENTREQUEST_0_PAYMENTACTION  "Sale"
#PAYERID  we get this from GetExpressCheckoutDetails

#STOP

def getshippingaddress(request):
  return render_to_response("getshippingaddress.html", locals())

def checkout(request):
#1620, 1621
  if not 'cart' in request.session:
    return home(request)

  sampleAddressDictionary={}
  sampleAddressDictionary['recipientName']="Scott Lobdell"
  sampleAddressDictionary['address1']="4305 Fremont Dr"
  sampleAddressDictionary['address2']=""
  sampleAddressDictionary['addressTownOrCity']="Killeen"
  sampleAddressDictionary['stateOrCountry']="TX"
  sampleAddressDictionary['postalOrZipcode']="76549"
  sampleAddressDictionary['country']="USA"
  sampleAddressDictionary['textOnReverse']=""

  newOrderId=createPwintyOrder(sampleAddressDictionary)
#user puts in shipping infp
#shipping info creates a pwinty order
#user is directed to a confirmation page
#user places the order through paypal
#paypal ipn sends back the order id
#order id gets submitted
  for iterator in request.session['cart']:
    if iterator['size']!="digital":
      addPhotoToPwintyOrder(newOrderId, iterator)

  success, message=submitPwintyOrder(newOrderId)
  if success:
    return HttpResponse("worked!")
  else:
    return HttpResponse(checkPwintyOrder(newOrderId))
  return render_to_response("checkout.html", locals())

def revieworder(request):
  title="Review Order"
  def pToS(key):
    request.session[key]=request.POST[key]
  if request.method=="POST":
    pToS('firstname')
    pToS('lastname')
    pToS('address1')
    pToS('address2')
    pToS('city')
    pToS('state')
    pToS('zipcode')
    pToS('email')
    pToS('phone')

  message=""
  if request.method=="GET":
    if "fail" in request.GET:
      message="There was an error processing your credit card.  Please ensure that you have input the proper data."
#  addressDict={}
#  addressDict['recipientName']=request.session['firstname']+" "+request.session['lastname']
#  addressDict['address1']=request.session['address1']
#  addressDict['address2']=request.session['address2']
#  addressDict['addressTownOrCity']=request.session['city']
#  addressDict['stateOrCountry']=request.session['state']
#  addressDict['postalOrZipcode']=request.session['zipcode']
#  addressDict['country']="USA"
#  newOrderId=createPwintyOrder(addressDict)
  shipping=0.0
  if 'cart' in request.session:
    for iterator in request.session['cart']:
      if not "dig" in iterator['size']:
        shipping=float(shippingPrice)
  if 'greetingcards' in request.session:
    for iterator in request.session['greetingcards']:
      shipping=float(shippingPrice)



#user puts in shipping infp
#shipping info creates a pwinty order
#user is directed to a confirmation page
#user places the order through paypal
#paypal ipn sends back the order id
#order id gets submitted
  allPictures=[]
  final=""
  if 'cart' in request.session:
    for iterator in request.session['cart']:
    #if iterator['size']!="digital":
      #retString=addPhotoToPwintyOrder(newOrderId, iterator)
      newPicture=Picture(map=Map.objects.get(id=iterator['pictureId']), size=iterator['size'], quantity=iterator['quantity'], matteGloss=iterator['matteGloss'])
      allPictures.append(newPicture)
      newPicture.save()
  #success=submitPwintyOrder(newOrderId) xxx
  readyToShip=ReadyToShip(orderNumber=0)
  readyToShip.email=request.session['email']
  readyToShip.save()
  for iterator in allPictures:
    readyToShip.pictures.add(iterator)
  readyToShip.save()

  request.session['readyToShip']=readyToShip
  request.session.modified = True  #force save
  cartDict={}
  prices=getPriceDict()
  debugString=""
  if 'cart' in request.session:
    request.session['cart']=adjustPricesByBoat(request.session['cart'])
    for iterator in request.session['cart']:
      key=iterator['size']
      if key in cartDict:
        cartDict[key]["quantity"]=cartDict[key]["quantity"]+int(iterator['quantity'])
        cartDict[key]["price"]=cartDict[key]["price"]+int(iterator['quantity'])*float(iterator["price"])
      else:
        cartDict[key]={}
        cartDict[key]["quantity"]=int(iterator['quantity'])
        cartDict[key]["price"]=float(iterator["price"])*int(iterator['quantity'])
  for key, value in cartDict.items():
    for key2, val2 in value.items():
      debugString+=key.__str__()+"...."+key2.__str__()+"...."+val2.__str__()+"<br/>"
#  return HttpResponse(debugString)
  if 'greetingcards' in request.session:
    for iterator in request.session['greetingcards']:
      key=iterator['size']
      if key in cartDict:
        cartDict[key]["quantity"]=cartDict[key]["quantity"]+int(iterator['quantity'])
        cartDict[key]['price']=cartDict[key]["price"]+int(iterator['quantity'])*float(iterator['price'])
      else:
        cartDict[key]={}
        cartDict[key]["quantity"]=int(iterator['quantity'])
        cartDict[key]["price"]=float(iterator['price'])*int(iterator['quantity'])
  total=0.0
  for key, value in cartDict.items():
    price=float(prices[key])
    cartDict[key]["price"]=round(float(cartDict[key]["price"]),2)
    total=total+float(cartDict[key]["price"])
  salesTaxRate=0
  if request.session['state'].lower()=="fl":
    salesTaxRate=0.06
  salesTax=salesTaxRate*total
  total+=salesTax
  totalPlusShipping=total+shipping
  return render_to_response("revieworder.html", locals())

def about(request):
  tab=5
  return render_to_response("about.html", locals())

def fetchPictureFromMapObject(mapObject, ftpObject):
  ftp=ftpObject
  r=StringIO()
  f=mapObject.ftpName
  ftp.retrbinary('RETR '+f, r.write)
  img=None
  img=Image.open(StringIO(r.getvalue()))
  return img

def submitLocalOrder(pictureObject, ftpObject, fullAddress, specialInstructions, originalOrder):
  email=EmailMessage()
  email.subject="Online Order Placed!"
  email.body=""
  email.body=email.body+"Order ID:  "
  email.body=email.body+originalOrder.id.__str__()+"\n"
  email.body=email.body+"The attached image has just been ordered:\n"
  email.body=email.body+originalOrder.cardType+"  **** **** **** "+originalOrder.lastFour+" exp "+originalOrder.expMonth+"/"+originalOrder.expYear+"\n"
  email.body=email.body+"Quantity: "+pictureObject.quantity.__str__()+"\n"
  email.body=email.body+"Size: "+pictureObject.size+"\n"
  email.body=email.body+"Matte or Gloss: "+pictureObject.matteGloss+"\n"
  email.body=email.body+"Contact Phone: "+originalOrder.phone.__str__()+"\n"
  email.body=email.body+"Email: "+originalOrder.readyToShip.email.__str__()+"\n"
  email.body=email.body+"\nAddress: \n\n"+fullAddress
  email.body=email.body+"\n\nSpecial Instructions for this order: "+specialInstructions
  email.body=email.body+"\n\nDate of Photo: "+pictureObject.map.watermarkName[0:10]
  email.body=email.body+"\n\n\nOriginal File Name: \"ftp://"+host+"/"+pictureObject.map.ftpName.replace(" ", "%20")+"\"\n"
  email.from_email="Boat Pix <no-reply@boatpix.com>"
  emailTo=["sales@boatpix.com","boatpix@aol.com","heliacademy@aol.com","itsallen65@yahoo.com", "scott.lobdell@gmail.com"]
  #emailTo=["scott.lobdell@gmail.com"]
#CHANGEME
  email.to=emailTo
  if ftpObject:
    randomName=""
    for j in range(0,40):
      var=random.randint(0,25)+65
      randomName=randomName+chr(var)
    randomName=randomName+".jpg"

#    originalImageName=pictureObject.map.ftpName
#    originalImageName=originalImageName.replace("\\","/").split("/")
#    originalImageName=originalImageName[len(originalImageName)-1]

#    image=fetchPictureFromMapObject(pictureObject.map, ftpObject)
#    image.save(imageDirectory+originalImageName,"jpeg")
#    email.attach_file(imageDirectory+originalImageName)

    email.attach_file(imageDirectory+pictureObject.map.watermarkName)

#  email.attach('image.jpg', list(imageData.getdata()), "image.jpg")
  email.send()
  if attachImage:
#    os.system('rm '+ imageDirectory+randomName)
    pass

########################################
def submitPaymentGoEMerchant(postDict):
  baseURL="secure.goemerchant.com"
  destinationURL="/secure/gateway/direct.aspx"

  postDict['Merchant']="45631"

  import httplib, urllib, simplejson
  params = urllib.urlencode(postDict)
  headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
  conn = httplib.HTTPSConnection(baseURL+":443")
  conn.request("POST", destinationURL, params, headers)

  response = conn.getresponse()

  data=response.read()
  conn.close()
  if "Transaction Results Successful" in data:
    return True, data
  else:
    return False, data

##########################################

from threading import Thread

class greetingEmailer(Thread):
  def __init__(self, greetingCardArray, originalOrder):
    Thread.__init__(self)
    self.greetingCardArray=greetingCardArray
    self.originalOrder=originalOrder

  def run(self):
    for itemDict in self.greetingCardArray:
      email=EmailMessage()
      email.subject="Greeting Card Order Delivery!"
      email.body=""
      email.body=email.body+"The attached greeting card has just been ordered:\n"
      email.body=email.body+"Credit Card Info:\n"
      email.body=email.body+self.originalOrder.cardType+"  **** **** **** "+self.originalOrder.lastFour+" exp "+self.originalOrder.expMonth+"/"+self.originalOrder.expYear+"\n"
      email.body=email.body+itemDict['size']
      email.body=email.body+"Quantity: "+itemDict['quantity'].__str__()+"\n"
      email.body=email.body+"Text: \n\n"
      email.body=email.body+itemDict['line1']+"\n"
      email.body=email.body+itemDict['line2']+"\n"
      email.body=email.body+itemDict['line3']+"\n\n"
      email.body=email.body+"Boat Name: "+itemDict['boatName']+"\n"
      email.body=email.body+"Sail Number: "+itemDict['sailNumber']+"\n"
      email.body=email.body+"Boat Make: "+itemDict['boatMake']+"\n"
      email.body=email.body+"Length: "+itemDict['length']+"\n"
      email.body=email.body+"Year: "+itemDict['year'].__str__()+"\n\n"
      email.body=email.body+"First Name: "+itemDict['firstName']+"\n"
      email.body=email.body+"Last Name: "+itemDict['lastName']+"\n"
      email.body=email.body+"Day Phone: "+itemDict['dayPhone']+"\n"
      email.body=email.body+"Evening Phone: "+itemDict['eveningPhone']+"\n"
      email.body=email.body+"Email Address: "+itemDict['emailAddress']+"\n"
      email.body=email.body+"Greeting Card Ordered: "+itemDict['picture']+"\n"
      email.body=email.body+"Special Instructions: "+itemDict['comments']+"\n"
      email.body=email.body+"\nShipping Address: \n"+self.originalOrder.address+"\n"
      email.from_email="Boat Pix <no-reply@boatpix.com>"
      emailTo=["sales@boatpix.com","boatpix@aol.com","heliacademy@aol.com","itsallen65@yahoo.com"]
      #emailTo=["scott.lobdell@gmail.com"]
  #for filename in os.listdir(greetingCardDirectory):
   # allCards.append(filename)
      email.to=emailTo
      email.attach_file(greetingCardDirectory+itemDict['picture'])


#  email.attach('image.jpg', list(imageData.getdata()), "image.jpg")
      email.send()
      import datetime
      from django.core.mail import send_mail
      send_mail("Order Completed", "greeting cards were just ordered", 'administrator@oraclefitness.com', ["scott.lobdell@gmail.com"], fail_silently=False)
class orderEmailer(Thread):
  def __init__(self, readyToShipObject, cartArray, postData, greetingCardArray, originalOrder):
    Thread.__init__(self)
    self.readyToShip=readyToShipObject
    self.cartArray=cartArray
    self.originalOrder=originalOrder
    self.postData=postData
    self.greetingCardArray=greetingCardArray
  def run(self):#change back to run
    import datetime
    from django.core.mail import send_mail
    receiptMessage="This email serves as your receipt with BoatPix.com\n"
    receiptMessage=receiptMessage+"Date of purchase: "+datetime.datetime.now().__str__()[0:16]+"\n"
    receiptMessage=receiptMessage+"Order Number: "+self.originalOrder.id.__str__()+"\n"
    receiptMessage=receiptMessage+"Items Ordered: \n"
    prices=getPriceDict()

    for iterator in self.cartArray:
      iterator['price']=prices[iterator['size']]
    self.cartArray=adjustPricesByBoat(self.cartArray)
    for iterator in self.cartArray:
      lineString=""
      lineString=iterator['quantity'].__str__()+"\t"+iterator['size']+"\t"+iterator['matteGloss']+"\t\t$"+(int(iterator['quantity'])*float(iterator['price'])).__str__()+", Picture ID: "+iterator['pictureId']
      receiptMessage=receiptMessage+lineString+"\n"
    for iterator in self.greetingCardArray:
      lineString=""
      lineString=iterator['quantity'].__str__()+"\t"+iterator['size']+"\t\t$"+(int(iterator['quantity'])*float(iterator['price'])).__str__()
      receiptMessage=receiptMessage+lineString+"\n"
    allPictures=self.readyToShip.pictures.select_related('map').all()
    allDigitalOrder=True
    containsDigital=False
    for iterator in allPictures:
      if "dig" in iterator.size:
        containsDigital=True
      if not "dig" in iterator.size:
        allDigitalOrder=False
    postData=self.postData
    if not allDigitalOrder:
      receiptMessage=receiptMessage+"Shipping: $25.00\n"

    receiptMessage=receiptMessage+"Total amount charged: $"+postData['totalPlusShipping']+"\n\n"
    receiptMessage=receiptMessage+"Billing information: \n"
    receiptMessage=receiptMessage+self.postData['fullName']+"\n"+self.postData['address1']+" "+self.postData['address2']+"\n"+self.postData['city']+", "+self.postData['state']+" "+self.postData['zip']+"\n"
    send_mail("Boatpix.com Receipt", receiptMessage, 'Boat Pix <no-reply@boatpix.com>', [self.readyToShip.email], fail_silently=False)
    ftp=FTP()
    ftp.connect(host, port=ftpPort)
    ftp.login(username, password)

    fullAddress=postData['fullName']+"\n"+postData['address1']+"\n"+postData['address2']+"\n"+postData['city']+"\n"+postData['zip']
    specialInstructions=postData['specialInstructions']
    for iterator in allPictures:
      if not "dig" in iterator.size:
        allDigitalOrder=False
        submitLocalOrder(iterator, ftp, fullAddress, specialInstructions, self.originalOrder)
      else:
        emailPicture(iterator, self.readyToShip.email, ftp)
    ftp.quit()
    #success=True
    success=True
    if success:



      pass
#      send_mail("Order Completed", "This is the programmer's notification that an order was completed.  Yay, money!", 'administrator@oraclefitness.com', ["scott.lobdell@gmail.com"], fail_silently=False)
    else:
      error=checkPwintyOrder(pwintyOrderNumber)

      send_mail("Order Failed", "junk\n"+error, 'administrator@oraclefitness.com', ["scott.lobdell@gmail.com"], fail_silently=False)

def checkForDuplicateOrders(postData, sessionData):
  lastFour=postData['cardNumber'].replace(" ","")[12:16]
  name=somethingInSession
  address=somethingInSession
  total=postData['totalPlusShipping']
  cv2=postData['cvv2']
  expMonth=postData['month']
  expYear=postData['year']
  cardType=postData['cardType']
#  possibleOrders=Order.objects.filter(

def placeOrder(request):
  def savegreetingcardorder(inList, originalOrder):
    for itemDict in inList:
      newOrder=GreetingCardOrder()
      newOrder.picture=itemDict['picture']
      newOrder.quantity=int(itemDict['quantity'])
      newOrder.size=itemDict['size']
      newOrder.line1=itemDict['line1']
      newOrder.line2=itemDict['line2']
      newOrder.line3=itemDict['line3']
      newOrder.price=float(itemDict['price'])
      newOrder.boatName=itemDict['boatName']
      newOrder.sailNumber=itemDict['sailNumber']
      newOrder.boatMake=itemDict['boatMake']
      newOrder.length=itemDict['length']
      try:
        newOrder.year=int(itemDict['year'])
      except:
        newOrder.year=0#TODO: fix this
      newOrder.firstName=itemDict['firstName']
      newOrder.lastName=itemDict['lastName']
      newOrder.dayPhone=itemDict['dayPhone']
      newOrder.eveningPhone=itemDict['eveningPhone']
      newOrder.emailAddress=itemDict['emailAddress']
      newOrder.comments=itemDict['comments']
      newOrder.datetime=datetime.datetime.now()
      newOrder.order=originalOrder
      newOrder.save()

  freeOrdering=False
  title="Order Complete!"
  if request.method=="POST":
    request.session['specialInstructions']=request.POST['specialInstructions']
    myString=""
    for key, value in request.POST.items():
      myString=myString+key+":    "+value+"<br/>"

    readyToShip=request.session['readyToShip']
    postDict={}
    postDict['OrderId']=readyToShip.id.__str__()
    postDict['total']=request.POST['totalPlusShipping']
    postDict['URL']="http://boatpix.com"
    postDict['Cardname']=request.POST['cardType']
    fullCard=request.POST['cardNumber'].replace(" ","")

    postDict['Cardnum1']=fullCard[0:4]
    postDict['Cardnum2']=fullCard[4:8]
    postDict['Cardnum3']=fullCard[8:12]
    postDict['Cardnum4']=fullCard[12:16]
    postDict['NameonCard']=request.POST['fullName']
    postDict['Cardstreet']=request.POST['address1']+" "+request.POST['address2']
    postDict['Cardcity']=request.POST['city']
    postDict['Cardzip']=request.POST['zip']
    postDict['Cardcountry']="US"
    postDict['Cardstate']=request.POST['state']
    postDict['CardexpM']=request.POST['month']
    postDict['CardexpY']=request.POST['year']
    postDict['CVV2']=request.POST['cvv2']
    success=False
    if not freeOrdering:
      success, data=submitPaymentGoEMerchant(postDict)
      if not success:
        startIndex=data.index("authresponse")
        data=data[startIndex:len(data)]
        endIndex=data.index("&")
        data=data[0:endIndex]
        data=data.replace("authresponse=","")
        data=data.replace("+",' ')
    else:
      success=True

    if not success:
      return HttpResponseRedirect("../revieworder/?fail=1&data="+data)
#    try:
    if success:
      currentCart=[]
      if 'cart' in request.session:
        for iterator in request.session['cart']:
          currentCart.append(iterator)
      greetingCardArray=[]
      if 'greetingcards' in request.session:
        for iterator in request.session['greetingcards']:
          greetingCardArray.append(iterator)

      postData=request.POST
      completedOrder=Order()
      completedOrder.orderNumber=0
      completedOrder.name=postData['first_name']+" "+postData['last_name']
      completedOrder.address=postData['address1']+"\n"+postData['address2']+"\n"+postData['city']+"\n"+postData['state']+"\n"+postData['zip']
      completedOrder.total=postData['totalPlusShipping']
      completedOrder.datetime=datetime.datetime.now()
      completedOrder.readyToShip=readyToShip
      fullCard=request.POST['cardNumber'].replace(" ","")
      completedOrder.lastFour=fullCard[12:16]
      completedOrder.cv2=request.POST['cvv2']
      completedOrder.expMonth=request.POST['month']
      completedOrder.expYear=request.POST['year']
      completedOrder.cardType=request.POST['cardType']
      completedOrder.phone=request.POST['phone']
      completedOrder.save()


      newThread=orderEmailer(readyToShip, currentCart, postData, greetingCardArray, completedOrder)
      newThread.start()
      anotherThread=greetingEmailer(greetingCardArray, completedOrder)
      anotherThread.start()

      for iterator in currentCart:
        iterator["map"]=Map.objects.get(id=int(iterator['pictureId']))
      if 'greetingcards' in request.session:
        savegreetingcardorder(request.session['greetingcards'], completedOrder)
      if 'cart' in request.session:
        del request.session['cart']
      if 'greetingcards' in request.session:
        del request.session['greetingcards']
    else:
#    except Exception, e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      message=(exc_type, fname, exc_tb.tb_lineno)
      from django.core.mail import send_mail
      send_mail("COMPLETE FAILED", message, 'administrator@oraclefitness.com', ["scott.lobdell@gmail.com"], fail_silently=False)

  return render_to_response("placeorder.html", locals())
def printscreen(request):
  message="While print screen functionality still works, if we continue to experience users taking BoatPix photos in this manner, we'll be forced to find new ways of protecting our images or disabling print screen functionality.  Sorry, but we have to be able to sell our photos for the price listed in order to deliver products to you and remain profitable to fund the business that we're passionate about!  Thanks for understanding."
  from django.core.mail import send_mail
  send_mail("someone tried to print screen", "junk for now","Boat Pix <no-reply@boatpix.com", ["scott.lobdell@gmail.com"], fail_silently=False)
  return render_to_response("success.html", locals())
def basicEmail(postDict):
  from django.core.mail import send_mail
  message=""
  for key, value in postDict.items():
    message=message+key+":    "+value+"\n"
  emailTo=["sales@boatpix.com","boatpix@aol.com","heliacademy@aol.com","itsallen65@yahoo.com", "scott.lobdell@gmail.com"]
  send_mail("Boatpics.com Generated Message", message, 'Boat Pix <no-reply@boatpix.com>', emailTo, fail_silently=False)


def contact(request):
  tab=6
  title="Contact Us"
  if request.method=="POST":
    basicEmail(request.POST)
    message="Request received!  We'll get back to you shortly"
    return render_to_response("success.html", locals())
  return render_to_response("contact.html", locals())

def paypal(request):
    from myproject.paypal.standard.forms import PayPalPaymentsForm
    from django.conf import settings
    from django.core.urlresolvers import reverse


    # What you want the button to do.

    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": "69.00",
        "item_name": "Photo Collection",
        "invoice": "unique-invoice-id",
        "notify_url": "http://pictureblimp.com/ipn",
        "return_url": "http://pictureblimp.com/ordercomplete/",
        "cancel_return": "http://pictureblimp.com/cart/",
    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form.sandbox()}
    return render_to_response("paypal.html", context)


def cart(request):
  title="Cart"
  #return HttpResponse(request.POST)
  tab=7
  if request.method=="POST":
    toRemove=[]
    greetingsToRemove=[]
    for key, value in request.POST.items():
      if "_" in key:
        twoValues=key.split("_")
        size=twoValues[0]
        pictureId=twoValues[1]
        if "." in pictureId: #it's a file
          for iterator in request.session['greetingcards']:
            if iterator['picture']==pictureId and iterator['size']==size:
              iterator['quantity']=request.POST[key]
              if int(request.POST[key])==0:
                greetingsToRemove.append(iterator)
        else:
          for iterator in request.session['cart']:
            if iterator['pictureId']==pictureId and iterator['size']==size:
              iterator['quantity']=request.POST[key]
              try:
                if int(request.POST[key])==0:
                  toRemove.append(iterator)
              except:
                  toRemove.append(iterator)
    for iterator in toRemove:
      request.session['cart'].remove(iterator)
    for iterator in greetingsToRemove:
      request.session['greetingcards'].remove(iterator)
    request.session.modified = True  #force save
    if 'empty' in request.POST:
      request.session['cart']=[]
      request.session['greetingcards']=[]
  if 'cart' in request.session:
    cartList=request.session['cart']
  else:
    cartList=[]
  for iterator in cartList:
    iterator['pictureUrl']="thumbnail-"+Map.objects.get(id=iterator['pictureId']).watermarkName
  prices=getPriceDict()
  for iterator in cartList:
    iterator['price']=prices[iterator['size']]
  cartList=adjustPricesByBoat(cartList)
  return render_to_response("cart.html", locals())


