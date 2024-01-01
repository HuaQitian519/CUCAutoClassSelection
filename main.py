from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
print("请确保你的设备上安装了Chrome浏览器，正在加载selenium驱动，请稍等！")
print("接下来请在打开的网页正常登陆，选择好选课页面后（进入选课页面），程序将自动关闭网页并开始提取信息！")
print('加载可能需要一些时间……')
# 设置Selenium驱动
service = Service(ChromeDriverManager().install())
print('驱动安装完成，准备打开网页……')
driver = webdriver.Chrome(service=service)

# 打开目标网站
driver.get("https://xsxk.cuc.edu.cn/xsxkapp/sys/xsxkapp/*default/index.do")

# 等待用户登录并且特定按钮出现
expected_button = WebDriverWait(driver, 1000000).until(
    EC.text_to_be_present_in_element(
        (By.TAG_NAME, 'body'),  # 检查<body>标签内的文本，您可以根据需要修改这个定位器
        '返回主页'  # 需要检查的文本
    )
)

# 此时可以认为用户已经登录，并且页面已更新
# 获取Cookie
cookies = driver.get_cookies()
token = driver.execute_script("return sessionStorage.getItem('token');")
info = driver.execute_script("return sessionStorage.getItem('studentInfo')")
studentcode = driver.execute_script("var studentInfo = JSON.parse(sessionStorage.getItem('studentInfo'));return studentInfo.code")
batchinfo = driver.execute_script("var studentInfo = JSON.parse(sessionStorage.getItem('studentInfo'));return studentInfo.electiveBatch.code")
print("Batchinfo:",batchinfo)
print("Token:", token)
print('Cookies:',cookies)
print('StudentCode:',studentcode)

# 关闭浏览器
driver.quit()
print('开始模拟查询信息！（PS：由于写代码时已经错过选课时间，无法爬取正常选课信息，故这里用查询来模拟抢课，后抢课时会将代码重写）')
url = 'https://xsxk.cuc.edu.cn/xsxkapp/sys/xsxkapp/elective/queryCourse.do'
cookiesinfo='_WEU='+cookies[1]["value"]+'; JSESSIONID='+cookies[0]['value']
# 请求头部
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': cookiesinfo,
    'Host': 'xsxk.cuc.edu.cn',
    'Origin': 'https://xsxk.cuc.edu.cn',
    'Referer': 'https://xsxk.cuc.edu.cn/xsxkapp/sys/xsxkapp/*default/grablessons.do?token=e43f275d-e3d1-44c1-95d9-f2123773eb86',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
    'X-Requested-With': 'XMLHttpRequest',
    'token': token
}

# POST请求的数据
data = {
    'querySetting': json.dumps({
        "data": {
            "studentCode": studentcode,
            "campus": "12",
            "electiveBatchCode": batchinfo,
            "isMajor": "1",
            "teachingClassType": "QXKC",
            "queryContent": ""
        },
        "pageSize": "10",
        "pageNumber": "0",
        "order": ""
    }),
    'electiveBatchCode': batchinfo
}

# 发送请求
response = requests.post(url, headers=headers, data=data)

# 检查响应
if response.status_code == 200:
    # 解析响应内容
    response = response.json()
    for item in response['dataList']:
        course_name = item.get('courseName', '未知课程')
        teacher_name = item.get('teacherName', '未知教师')
        teaching_place = item.get('teachingPlace', '未知地点')
        credit = item.get('credit', '未知学分')

        print(f"课程名称: {course_name}")
        print(f"教师姓名: {teacher_name}")
        print(f"教学地点: {teaching_place}")
        print(f"学分: {credit}")
        print("-" * 30)  # 分隔符
else:
    print("请求失败，状态码：", response.status_code)
