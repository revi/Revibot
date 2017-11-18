# Licensed under GFDL/CC BY SA 3.0 (Wikipedia License!)
# -*-  coding: utf-8  -*-
import sys, pywikibot
from pywikibot import pagegenerators
from pywikibot.compat import catlib
import time, os
import re, codecs, gc, threading
 
site = pywikibot.Site('ko')
err_cnt = 0

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "-d" :
    # 서버에서 무한 반복으로 돌릴 때에는 아래를 사용: | Use below when running infinitely running mode in the server (note:probably cron)
        while 1<2:
            err_cnt = 0
            update([u"의견 요청"],u"틀:의견 요청 목록",u"이 문서는 봇에 의해 갱신되고 있습니다. [[분류:위키백과 틀|{{PAGENAME}}]]").start()
            gc.collect() 
            time.sleep(300)
    else : 
        update([u"의견 요청"],u"틀:의견 요청 목록",u"이 문서는 봇에 의해 갱신되고 있습니다. [[분류:위키백과 틀|{{PAGENAME}}]]").start()
        gc.collect()
 
class update(threading.Thread):
  def __init__ ( self,templates,post_template,bottomtxt):
        self.templates = templates
        self.post_template = post_template
        self.bottomtxt = bottomtxt
        threading.Thread.__init__ ( self )
 
  def run(self):
    global err_cnt
    pages=[]
    message=''
    dic={}
    templates = self.templates
    bottomtxt ='%s' % self.bottomtxt
    post_template = self.post_template
    if len(templates)==1:
      regex ='%s' % templates[0]
    else:
      regex='('
      part=''
      for template in templates:
        regex+= part + template
        part='|'
      regex+=')'
    for template in templates:
      pagegen = pagegenerators.ReferringPageGenerator(pywikibot.Page(site, u'틀:%s' % template), onlyTemplateInclusion = True)
      for page in pagegen:
        pages.append(page)
    pages = sorted(set(pages))
    message =u''
    if pages:
      for page in pages:
        Time,line = pageparse(page,regex)
        dic[Time]=line
      keys= dic.keys()
      keys.sort(reverse=True)
      for key in keys:
        message +=u'%s' % dic[key]
    else:
      message = u'* 목록에 토론이 없습니다.'
    pagetext= u"'''아래의 토론들은 여러 편집자의 참여와 관심을 필요로 하고 있습니다.'''\n----\n<onlyinclude>%s\n</onlyinclude>\n%s" % (message,bottomtxt)
    templatepage = pywikibot.Page(site,'%s' % post_template )
    templatepage.put(pagetext, comment=u'수정, 현재 %s 개의 토론이 있습니다.' % str(len(pages) - err_cnt) )
    pywikibot.output('Update, %s current discussions\n Sleeping for 5 minutes' % str(len(pages) - err_cnt) )
    gc.collect() 

def pageparse(page,regex):
  pywikibot.output(page.title())
  global err_cnt
  try:
    message =''
    text    = page.get()
    Time    = time.time()
    reason  = ''
    section = ''
    dic     = {}
    g = re.search(u"문단(|\s)=.*?\!\!",text,re.I)
    # wikipedia.output(g)
    g = g.group(0).split('=')[1]
    g = g.split('!')[0]
    dic['section'] = g.strip()
    g2 = re.search(u"사유(|\s)=.*?\!\!",text,re.I)
    g2 = g2.group(0).split('=')[1]
    g2 = g2.split('!')[0]
    dic['reason'] = g2.strip()
    g3 = re.search(u"시각(|\s)=.*?\}\}",text,re.I)
    g3 = g3.group(0).split('=')[1]
    g3 = g3.split('}')[0]
    dic['time'] = g3.strip()
    if dic.has_key('reason'):
      reason = dic['reason']
    if dic.has_key('time'):
      Time = dic['time']
      st = Time.split() # 2008년 1월 30일 (수) 23:01 (KST)
      Time = st[0][:-1]+' '+st[1][:-1]+' '+st[2][:-1]+' '+st[4][:2]+' '+st[4][3:]
      edittime = time.strptime(Time, u"%Y %m %d %H %M")
      Time = time.mktime(edittime)
    if dic.has_key('section'):
      section = dic['section']
      section = re.sub(' ','_',section)
      section = re.sub('\[','',section)
      section = re.sub('\]','',section)
      #page_title_to_read = ''  
      #if page.title()[:2] == u'백:' :
        #page_title_to_read = '위키백과' + page.title()[1:]
      link = u'\n* [[%s#%s|%s]] - ' % (page.title(),section,page.title())
      #link = u'\n* [[%s#%s|%s]] - ' % (page.title(),section,page_title_to_read())
    else:
      link = u'\n* [[%s]] ' % page.title()
    if Time < (time.time()- 2592000):
      text = re.sub('\{\{'+regex+'(.*?)\}\}','',text)
      page.put(text,comment= u'오래된 의견 요청 제거')
      err_cnt = err_cnt + 1 
      gc.collect() 
      return '',''
    message =u'%s%s' % (link,reason)
    message = re.sub('&#124;','|',message)
    gc.collect() 
    return Time, message
  except: 
    text = page.get()
    text = re.sub('\{\{'+regex+'(.*?)\}\}',u"{{의견 요청 오류}}",text)
    page.put(text,u"의견 요청 오류")
    err_cnt = err_cnt + 1
    print("ERROR COUNT:", err_cnt)
    gc.collect() 
    return '',''
 
if __name__ == '__main__':
  try:
    main()
  finally:
    pywikibot.stopme()