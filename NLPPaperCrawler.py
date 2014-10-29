'''
名称 :"NLP论文爬虫"
版本 :1.0
作者 :heyu
Email:heyucs@yahoo.com
'''

#coding=utf-8
import urllib 
import urllib2
import re
import thread
import os
import time
import codecs

def filenameFilter(filename):
        result, number = re.subn(r'[\/:*?"><|’]', '', filename)
        return result
                                 


def downPaper(url, filename):
	urllib.urlretrieve(url, filename)
	f = urllib2.urlopen(url) 
	data = f.read()	
	with open(filename, "wb") as code:
		code.write(data)


def getKeyword():
	keyDic = []
	keyStr = str(raw_input(u'请输入您要查找文章的关键字(以空格分隔):\n'))
	for key in keyStr.split():
		keyDic.append(key)
	return keyDic


def getPaperUrl(rooturl):
	response = urllib2.urlopen(rooturl)
	html = response.read()
	pattern = r'<p><a href=.+>.+</a>.*: <b>.+</b><br><i>.+</i>'
	regex = re.compile(pattern)
	urlList = re.findall(regex,html)
	return urlList

def getFileName(url):
	regexpr = re.compile(r'<p><a href=["]*(.*?)["]*>(.*?)</a>[: ]',re.DOTALL)
	filename = regexpr.search(url)
#	print filename.group(1),filename.group(2)
	return filename.group(1)

def getAuthor(url):
	regexpr = re.compile(r': <b>(.*?)</b><br>',re.DOTALL)
	authors = regexpr.search(url)
#	print authors.group(1)
	return authors.group(1)

def getPaperName(url):
	regexpr = re.compile(r'<br><i>(.*?)</i>',re.DOTALL)
	papername = regexpr.search(url)
#	print papername.group(1)
	return papername.group(1)



def filterUrl(urlList, keywordDic):
	newUrlList = []
	for url in urlList:
		filename  = getFileName(url)  
		authors   = getAuthor(url)      #可用于过滤作者
		papername = getPaperName(url)
		if len(keywordDic) != 0 :
			flag = 0
			for i in range(0,len(keywordDic)):
				ret = papername.lower().find(keywordDic[i].lower())
				if ret == -1:
					flag = 1
			if flag == 0:
				newUrlList.append(url)
	return newUrlList


def downloadPaper(rooturl,urlList,dic,loc):
	no = 0
	for url in urlList:
		filename  = getFileName(url)  
		authors   = getAuthor(url) 
		papername = getPaperName(url)
		firstauthor = authors.split(';')[0]
#		print rooturl+filename
		papername = filenameFilter(papername)
		downPaper(rooturl+filename,dic+loc[2:5]+'_'+firstauthor+'_'+papername+'.pdf')
		no += 1
		print str(no)+u' 正在下载论文：' + papername


def getConfLoc(url):
	regexpr = re.compile(r'<a href="(.*?)">.*</a>',re.DOTALL)
	loc = regexpr.search(url)
	return loc.group(1)

def getConfTime(url):
	regexpr = re.compile(r'<a href=".*">(.*?)</a>',re.DOTALL)
	years = regexpr.search(url)
	time = years.group(1)
	if time == '74-79':
		return '1974-1979'
	else:
		if int(time)>50:
			return '19'+time
		else:
			return '20'+time



def showOneConf(pattern,html,regex,locMap):
	regexpr = re.compile(pattern,re.DOTALL)
	block = regexpr.search(html)
	List = re.findall(regex,block.group(1))
	no = len(locMap)+1
	for i in range(len(List)):
		print '['+ str(no) +']:' + getConfTime(List[i]),
		if no == 72:
			locMap[no] = getConfLoc(List[i])+'/'
		else:
			locMap[no] = getConfLoc(List[i])
		no += 1
	print '\n'

def showAllConference(rooturl, locMap):
	response = urllib2.urlopen(rooturl)
	html = response.read()
	pattern = r'<a href="[A-Z0-9/]+">[-0-9]+</a>'
	regex = re.compile(pattern)
	no = 1
	CLpattern = r'<tr><th title="Computational Linguistics Journal">CL:</th>(.*?)</td></tr>'
	ACLpattern = r'<tr><th title="ACL Annual Meeting">ACL:</th>(.*?)</td></tr>'
	EACLpattern = r'<tr><th title="European Chapter of ACL">EACL:</th>(.*?)</td></tr>'
	NAACLpattern = r'<tr><th title="North American Chapter of ACL">NAACL:</th>(.*?)</td></tr>'
	EMNLPpattern = r'<tr><th title=.*>EMNLP:</th>(.*?)</td></tr>'
	COLINGpattern = r'<tr><th title=.*>COLING:</th>(.*?)</td></tr>'
	print 'CL：'
	showOneConf(CLpattern, html, regex, locMap)
	print 'ACL：'
	showOneConf(ACLpattern, html, regex, locMap)
	print 'EACL：'
	showOneConf(EACLpattern, html, regex, locMap)
	print 'NAACL：'
	showOneConf(NAACLpattern, html, regex, locMap)
	print 'EMNLP：'
	showOneConf(EMNLPpattern, html, regex, locMap)
	print 'Coling：'
	showOneConf(COLINGpattern, html, regex, locMap)	


def getLocation(rooturl):
	locMap = {}
	locList = []
	showAllConference(rooturl, locMap)
	idStr = str(raw_input(u'请输入您要下载的会议编号,以空格分隔,可以输入连续编号，比如1-30:\n'))
	idList = idStr.split()
	for id in idList:
		spanSet = id.split('-')
		if len(spanSet) == 2:
			for i in range(int(spanSet[0]),int(spanSet[1])+1):
				locList.append(locMap[i])
		else:
			locList.append(locMap[int(id)])
	return locList


def getKeyStr(keywordDic):
	ss = ''
	for key in keywordDic:
		ss += key
		ss += '_'
	return ss


root_url = 'http://www.aclweb.org/anthology/'


if __name__ == '__main__':
	locList = getLocation(root_url)
	keywordDic = getKeyword()  #获取检索关键字
	no = 1
	dic = getKeyStr(keywordDic)
	currTime = time.strftime('%Y%m%d-%H%M%S',time.localtime(time.time()))
	dic += currTime
	os.mkdir(dic)
	dic += '/'
	for loc in locList:
		downurl = root_url + loc
		print u'确认下载网址:', downurl
		urlList = getPaperUrl(downurl)
		print len(urlList)
		new_urlList = filterUrl(urlList,keywordDic)
		print u'过滤完成 ' + str(len(urlList)) + ' -> ' + str(len(new_urlList))
		downloadPaper(downurl,new_urlList,dic,loc)
		print u'下载完成' + str(no) + u'个会议任务'
	print 'Done!^_^'

