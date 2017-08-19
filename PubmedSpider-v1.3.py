#coding:utf-8
#代码功能简介：
#===================================================
#本代码为PubMed网站的爬虫机器人，可以根据你在pubmed上
#搜索关键词返回的网页自动下载几乎所有搜索结果里的文章的
#信息。这些信息包括文章title，PMID，作者、作者信息，发
#表的期刊，发表日期，摘要共7项主要信息。并根据情况自动
#发邮件通知你抓取进度。
#仅供研究医药行业动态，请勿爬取大量信息！
#如有利益冲突，请告知。
#版本1.3 --提高了稳定性
#时间：2017年8月 
#XMU
#Author:Hong Yikai 
#me@hongyikai.com
#www.hongyikai.com
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


#你的selenium的驱动地址：
driverUrl='D:\pymodules\chromedriver.exe'
#driverUrl='D:\pypackages\chromedriver.exe'

#你的pubmed网址（先按规则搜索，copy第一个结果页面到这里）：
webUrl='https://www.ncbi.nlm.nih.gov/pubmed?term=((epilepsy%5BTitle%5D)%20OR%20epileptic%5BTitle%5D)%20OR%20seizure%5BTitle%5D'

#爬取PMID的时候可能出现错误，可以从这里重新开始。"0"为跳过下载PMID，仅在PMId下载完后设置
startPage=0
#startPage=int(input("0为下载PMID文献信息，n为开始下载第n页PMID \n 请输入开始爬取PMID的页面："))
part2Start=int(input('请输入从第几个PMID开始下载信息:'))

#第一部分用到的函数
#================================================================================
#将pubmed搜索结果的每页显示20项改成200项，减少翻页次数
def items_per_page():
    #点击pubmed上“Per page”下拉菜单
    time.sleep(1)
    tags_List=driver.find_elements_by_class_name("tgt_dark")
    i=1
    for tag_List in tags_List:
        if i==3:
            tag_List.click()
            break
        i+=1    
    time.sleep(0.3)
    #选择每页显示200项（Items per page），方便一次读取
    driver.find_element_by_id("ps200").click() 
    time.sleep(10)       

            
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


#翻到指定页面
def page_turning(page_target):
    driver.find_element_by_id("pageno").clear()
    time.sleep(0.3)
    driver.find_element_by_id("pageno").send_keys(page_target) #输入页码
    time.sleep(0.3)
    driver.find_element_by_id("pageno").send_keys(Keys.ENTER) #按回车键

#================================================================================


#第二部分用到的函数
#================================================================================
#函数获取文章信息并初步清洗后储存
def article_to_save():
    try:
        #获取PMID
        PMID=driver.find_element_by_class_name("rprtid").find_element_by_tag_name("dd").text
        PMID=re.findall(r"[0-9]+",PMID)
    except:
        return 'tryAgain'
#        print(PMID)

    #获取期刊来源
    try:
        journal=driver.find_element_by_class_name("cit").find_element_by_tag_name("a").get_attribute("title")
        journal=re.findall(r"[A-Z][A-Za-z \&\-\'\.]+",journal)
    except:
        journal=[""]
#        print(journal)
    
    #获取文章发表的日期信息,用正则比较好找
    try:
        publishDate=driver.find_element_by_class_name("cit").text
        publishDate=re.findall(r"[12]\d{3} [JFMASOND][a-z]{2} [0-1]*[0-9]*",str(publishDate))
        if len(publishDate) < 1:
            publishDate=[""]
    except:
        publishDate=[""]
#        print(publishDate)
    
    #获取文章title
    try:
        title=driver.find_element_by_class_name("abstract").find_element_by_tag_name("h1").text
        title=[title.strip("$.[]{}:*& '><?)(")]
    except:
        title=[""]
#        print(title)
        
#返回重试信息
    
    #获取文章摘要
    try:
        abstract=driver.find_element_by_class_name("abstr").text
    except:
        abstract=[""]
#    print(abstract)

    
    #获取作者名字,注意authList,作者可能有很多个
    try:
        authors=driver.find_element_by_class_name("auths").find_elements_by_tag_name("a")
        authorList=[]
        for author in authors:
            authorList.append(author.text)
    except:
        authorList=[""]
#    print(authorList)
    
    #获取作者信息
    try:
        hahahas=driver.find_element_by_class_name("afflist")
        hahahas.click()
        auth_infos=driver.find_element_by_class_name("afflist").find_elements_by_tag_name("dd")
        authInfo=[]
        for auth_info in auth_infos:
            authInfo.append(auth_info.text)
    except:
        authInfo=[""]
#    print(authInfo)
        
    #储存获取的信息
    MyPubmedData=open("D:/MyPubmedData.csv",'a',newline='',encoding='utf-8')
    MyPubmed = csv.writer(MyPubmedData)
    MyPubmed.writerow((PMID[0],journal[0],publishDate[0],title[0],authorList,authInfo,abstract))
    MyPubmedData.close()
    
    return 'done' #顺利运行到最后一步，返回一个信息
    
#储存获取失败的文章地址
def PMID_url_err_save(PMID_url):
    PmidUrlErr =open("D:/PmidUrlErr.csv",'a',newline='',encoding='utf-8')
    PmidUrlErr.write(PMID_url+'\n')
    PmidUrlErr.close() 
#================================================================================


#邮件通知进度用到的函数
#================================================================================
my_sender='xxx@gmail.com' #发件人邮箱账号
my_user='me@hongyikai.com' #收件人邮箱账号
def email_progress(myMessage):
    try:
        msg=MIMEText(myMessage,"plain","utf-8")
        msg['From']=formataddr(['高贵的小虫',my_sender]) #括号里的对应发件人邮箱昵称（str）、发件人邮箱账号
        msg['To']=formataddr(['Hong Yikai',my_user]) #括号里的对应收件人邮箱昵称（str）、收件人邮箱账号
        msg['Subject']="你家的小虫喊你回家吃饭" #邮件的主题，也可以说是标题
        server=smtplib.SMTP_SSL("xxx.xxx.com",25) #发件人邮箱中的SMTP服务器，端口是25,SSL加密则根据各网站服务器定义的写
        server.login(my_sender,"password") #括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender,[my_user,],msg.as_string()) #括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit() #这句是关闭连接的意思
        print("邮件已经发给%s"%my_user)
    except Exception: #如果try中的语句没有执行，则会执行下面
        print("邮件未发出")
#================================================================================




#第一部分开始：抓取PMID并储存下来
#================================================================================
if startPage != 0:
    driver = webdriver.Chrome(executable_path= driverUrl)
    driver.get(webUrl)
    time.sleep(15)
    items_per_page()
    time.sleep(10)
    pages=driver.find_element_by_id("pageno").get_attribute("last") #得到总页数
    pages=int(pages)
    print("总共有%d页需要储存"%pages)
    pageEnd= pages+1
    for page in range(startPage,pageEnd): #逐页获取PMID并储存
        while True: #不断重试直到获取到页面
            unknownErr=0 #错误计数
            try:
                progress=int(page/pages*100)
                print("正在跳转到第%d/%d页，PMID已下载：%d%%" %(page,pages,progress))
                page_turning(page) #翻到下一页
                time.sleep(10)
                PMID_to_save() #储存当前页面PMID 
                break
            except:
                print('本页面打开或者储存错误，正在重试')
                time.sleep(5)
                driver.back()
                time.sleep(30)
                unknownErr+=1
                if unknownErr==3:
                    email_progress('Hi,亲爱的主人，3次翻页或者获取、下载信息失败。我会一直重试的！') 
                    time.sleep(60)
                if unknownErr >5:
                    time.sleep(600) #如果尝试了5次还错误，就大大降低重试频率吧
                    
    driver.quit()
    
    #发邮件通知
    allPMIDs=(pages-1)*200 #PMID总数
    message='Hi,亲爱的主人，我找到了至少'+str(allPMIDs)+'个PMID，已全下载好了。当您收到这封邮件的时候我已经开始在爬文献信息了哦。拜~'
    email_progress(message)
#================================================================================




#第二部分开始：抓取每篇文章信息并储存
#================================================================================
driver = webdriver.Chrome(executable_path= driverUrl)
#driver.implicitly_wait(120) #智能等待

#统计有多少个PMID需要被下载，统计完后关闭PMID.csv
allPMIDs=0 
PMID_file =open("D:/PMID.csv",'r')
for PMID_line in PMID_file.readlines():
    allPMIDs+=1
PMID_file.close()
print('总共有%d篇文章需要下载'%allPMIDs)

#开始下载，需要重新打开PMID.csv，让指针从第一行开始计数
PMID_file =open("D:/PMID.csv",'r')
i=0 #显示正在处理第几个PMID的计数  
msgErrCount=0 #显示跳过了几个尝试失败的PMID
for PMID_line in PMID_file.readlines():  #每次读取一行PMID
    i+=1 
    unknownErr=0 #自动尝试获取次数，当失败达到3次自动跳过错误的PMID
    timeLapse=0.1 #调整等待时间
    while i>=part2Start: #获取并保存信息
        progress=int(i/allPMIDs*100)
        print("正在获取第%d/%d页。进度：%d%%"%(i,allPMIDs,progress))
        PMID_line = PMID_line.strip()
        PMID_url="https://www.ncbi.nlm.nih.gov/pubmed/"+str(PMID_line)
        driver.get(PMID_url) #打开网页
        time.sleep(timeLapse) #调整等待时间
        tryAgain=article_to_save() #基础信息获取失败会返回重试'tryAgain'
        if tryAgain=='done':
            break
        driver.close()
        timeLapse=3
        unknownErr+=1
        if unknownErr==2: #第二次尝试失败后，打开网页后等待30秒
            print('等待20秒后重试')    
            timeLapse=10
        if unknownErr==3: #第三次加载失败后报错并跳过
            print('3次尝试获取信息失败，自动跳过')
            msgErrCount+=1
            PMID_url_err_save(PMID_url) #储存跳过的PMID
            if msgErrCount==1: #看跳过了几个PMID
                msgErr='Hi,亲爱的主人，为您跳过'+str(msgErrCount)+'个PMID。'
                email_progress(msgErr)
            elif msgErrCount==10:
                msgErr='Hi,亲爱的主人，为您跳过'+str(msgErrCount)+'个PMID。'
                email_progress(msgErr)
            elif msgErrCount==int(allPMIDs*0.01):
                msgErr='Hi,亲爱的主人，为您跳过'+str(msgErrCount)+'个PMID。错误达到1%!'
                email_progress(msgErr)
            elif msgErrCount==int(allPMIDs*0.05):
                msgErr='Hi,亲爱的主人，为您跳过'+str(msgErrCount)+'个PMID。错误达到5%！！！！'
                email_progress(msgErr)
            break
        #超出精确值，退出文章信息下载。每次循环都会计算一次int(allPMIDs*0.05)，处女座的可以先把这个计算好再放进来。。
    if msgErrCount >= int(allPMIDs*0.05):
        break
    
PMID_file.close()

driver.quit()

#发邮件通知
message='Hi,亲爱的主人，我是您的机器人小虫，Pubmed上的文献资料已处理完。共为您爬取了'+str(allPMIDs)+'篇文章的摘要等信息。么么哒，快肥来查看数据吧！拜~'
email_progress(message)
#================================================================================


    









