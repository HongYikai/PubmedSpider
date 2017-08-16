#coding:utf-8
#代码功能简介：
#===================================================
#本代码为PubMed网站的爬虫机器人，可以根据你在pubmed上
#搜索关键词返回的网页自动下载几乎所有搜索结果里的文章的
#信息。这些信息包括文章title，PMID，作者、作者信息，发
#表的期刊，发表日期，摘要共7项主要信息。并根据情况自动
#发邮件通知你抓取进度。2017年08月
#仅供研究医药行业动态，请勿爬取大量信息！
#如有利益冲突，请告知。
  
#                作者：Hong Yikai
#                    厦门大学
#           联系邮箱：me@hongyikai.com
#               www.hongyikai.com
#===================================================
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re 
import csv

#导入处理发邮件的模块
import smtplib  
from email.mime.text import MIMEText
from email.utils import formataddr


#第一部分用到的函数
#================================================================================
#将pubmed搜索结果的每页显示20项改成200项，减少翻页次数
def items_per_page():
    #点击pubmed上“Per page”下拉菜单
    tags_List=driver.find_elements_by_class_name("tgt_dark")
    i=1
    for tag_List in tags_List:
        if i==3:
            tag_List.click()
            break
        i+=1    
    time.sleep(1)
    #选择每页显示200项（Items per page），方便一次读取
    driver.find_element_by_id("ps200").click()
    time.sleep(3)

#函数获取文章PMID并储存
def PMID_to_save():
    #读取信息
    PMID=[]
    articles=driver.find_elements_by_class_name("rslt") #定位到200篇文章信息的外层位置
    for article in articles:
        PMID.append(article.find_element_by_tag_name("dd").text) #获取文章的PMID
    #逐行储存信息
    PMID_index =open("D:/PMID.csv",'a',newline='')
    for pmid in PMID:
        PMID_index.write(pmid+'\n')
    PMID_index.close()

#翻页
def page_turning(page_target):
    pageNum=page_target
    driver.find_element_by_id("pageno").clear()
    driver.find_element_by_id("pageno").send_keys(pageNum) #输入页码
    time.sleep(0.1)
    driver.find_element_by_id("pageno").send_keys(Keys.ENTER) #按回车键
    time.sleep(0.1)
#================================================================================


#第二部分用到的函数
#================================================================================
#函数获取文章信息并初步清洗后储存
def article_to_save():
    #获取PMID
    PMID=driver.find_element_by_class_name("rprtid").find_element_by_tag_name("dd").text
    PMID=re.findall(r"[0-9]+",PMID)
    #获取期刊来源
    journal=driver.find_element_by_class_name("cit").find_element_by_tag_name("a").get_attribute("title")
    journal=re.findall(r"[A-Z][A-Za-z \&\-\']+",journal)  
    #获取文章发表的日期信息,用正则比较好找
    publishDate=driver.find_element_by_class_name("cit").text
    publishDate=re.findall(r"[12]\d{3} [JFMASOND][a-z]{2} [0-1]*[0-9]*",str(publishDate))
    #获取文章title
    title=driver.find_element_by_class_name("abstract").find_element_by_tag_name("h1").text
    title=[title.strip("$.[]{}:*& '><?)(")]
    #获取文章摘要
    try:
        abstract=driver.find_element_by_class_name("abstr").text
    except:
        abstract=[""]
    #获取作者名字,注意authList,作者可能有很多个
    try:
        authors=driver.find_element_by_class_name("auths").find_elements_by_tag_name("a")
        authorList=[]
        for author in authors:
            authorList.append(author.text)
    except:
        authorList=[""]    
    #获取作者信息
    try:
        driver.find_element_by_class_name("afflist").click()
        auth_infos=driver.find_element_by_class_name("afflist").find_elements_by_tag_name("dd")
        authInfo=[]
        for auth_info in auth_infos:
            authInfo.append(auth_info.text)
    except:
        authInfo=[""]
        
    #储存获取的信息
    MyPubmedData=open("D:/MyPubmedData.csv",'a',newline='',encoding='utf-8')
    MyPubmed = csv.writer(MyPubmedData)
    MyPubmed.writerow((PMID[0],journal[0],publishDate[0],title[0],authorList,authInfo,abstract))
    MyPubmedData.close()
#================================================================================


#邮件通知进度用到的函数
#================================================================================
my_sender='此处要填发件人邮箱' #发件人邮箱账号
my_user='me@hongyikai.com' #收件人邮箱账号
def email_progress(myMessage):
    try:
        msg=MIMEText(myMessage,"plain","utf-8")
        msg['From']=formataddr(['高贵的小虫',my_sender]) #括号里的对应发件人邮箱昵称（str）、发件人邮箱账号
        msg['To']=formataddr(['Hong Yikai',my_user]) #括号里的对应收件人邮箱昵称（str）、收件人邮箱账号
        msg['Subject']="你家的小虫喊你回家吃饭" #邮件的主题，也可以说是标题
        server=smtplib.SMTP_SSL("此处要填smtp服务器",此处是端口数字) #发件人邮箱中的SMTP服务器，端口是25,SSL加密则根据各网站服务器定义的写
        server.login(my_sender,"密码被我删了") #括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender,[my_user,],msg.as_string()) #括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit() #这句是关闭连接的意思
        print("邮件已经发给%s"%my_user)
    except Exception: #如果try中的语句没有执行，则会执行下面
        print("邮件未发出")
#================================================================================




#第一部分开始：抓取PMID并储存下来
#================================================================================
driver = webdriver.Chrome(executable_path='D:\pymodules\chromedriver.exe')
driver.get("https://www.ncbi.nlm.nih.gov/pubmed?term=((epilepsy%5BTitle%5D)%20OR%20epileptic%5BTitle%5D)%20OR%20seizure%5BTitle%5D")
print("正在打开页面")
driver.implicitly_wait(60) #智能等待30秒
items_per_page() #更改为每页显示200项结果
print("Pubmed页面已改为每页显示200项结果")
pages=driver.find_element_by_id("pageno").get_attribute("last") #得到总页数
pages=int(pages)
print("总共有%d页需要储存"%pages)
for page in range(2,pages): #逐页获取PMID并储存（最后一页不搞）
    PMID_to_save() #储存当前页面PMID
    page_turning(page) #翻到下一页
    progress=int(page/pages*100)
    print("第%d页，PMID已下载：%d%%" %(page,progress))
print("PMID已下载：100%")
driver.quit()
#发邮件通知
allPMIDs=(pages-1)*200 #PMID总数
message='Hi,亲爱的主人，我找到了'+str(allPMIDs)+'个PMID，已全下载好了。当你收到这封邮件的时候我已经开始在爬文献信息了哦。拜~'
email_progress(message)
#================================================================================


#第二部分开始：抓取每篇文章信息并储存
#================================================================================
i=1 #计数
unknownErr=0 #错误计数
PMID_file =open("D:/PMID.csv",'r')
driver = webdriver.Chrome(executable_path='D:\pymodules\chromedriver.exe')
driver.implicitly_wait(60)
for PMID_line in PMID_file.readlines():
    try:
        PMID_line = PMID_line.strip()
        PMID_url="https://www.ncbi.nlm.nih.gov/pubmed/"+str(PMID_line)
        print("开始处理第：%d页"%i)
        driver.get(PMID_url) #打开网页
        article_to_save() #调用函数读取信息并保存。
        progress=int(i/allPMIDs*100)
        print("第%d/%d页，已抓取：%d%%"%(i,allPMIDs,progress))
        time.sleep(0.1)
    except:
        unknownErr+=1
        if unknownErr==1:
            message='亲爱的主人，刚才发生了1个错误，目前正在抓取第'+str(i)+'页。进度:'+str(progress)+'%。'
            email_progress(message)
        elif unknownErr==100:
            message='亲爱的主人，已经发生了100个错误，吓死宝宝了！！！目前正在抓取第'+str(i)+'页。进度:'+str(progress)+'%。'
            email_progress(message)
        elif unknownErr==1000:
            message='Hi,亲爱的主人，刚刚发生第了1000个错误，目前正在抓取第'+str(i)+'页。进度:'+str(progress)+'%。快回来，快回来，快回来！重要的事情要说3遍！！'
            email_progress(message)
    finally:
        i+=1
PMID_file.close()
driver.quit()
#发邮件通知
PMID_count=str(i-unknownErr)
message='Hi,亲爱的主人，我是您的机器人小虫，好激动！Pubmed上的文章全部处理完毕。共为您下载了'+PMID_count+'篇文章的摘要等信息，另外有'+str(unknownErr)+'篇出现错误。我是不是棒棒哒！快肥来查看数据吧！拜~'
email_progress(message)
#================================================================================












