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


  allDates=Map.objects.filter(date__range=(now, endOfMonth))
  if existingId!=None:
    allDates=Map.objects.filter(date__range=(now, endOfMonth), latitude=currentObject.latitude, longitude=currentObject.longitude)
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


  for iterator in allM:
    currentDay=int((iterator.watermarkName.replace(pattern,""))[0:2]  )
    pictureDictionary[currentDay]="thumbnail-"+iterator.watermarkName

  return render_to_response("calendar.html", locals())
