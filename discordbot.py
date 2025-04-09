import discord
import time
from discord.ext import tasks
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# 디스코드 봇 토큰과 채널 ID
TOKEN = "MTM1OTQ4NTYwOTYxNzUyNjk4OQ.GIfZEs.ezQy7rnmnJzgQSauIlfZ1OMq2Gbek7xZDJrj30"
CHANNEL_ID = 1290287160687067226  # 디스코드 채널 ID (숫자만 입력)

# 가장 최근에 전송한 공지사항 ID (중복 전송 방지용)
last_notice_id = None

# 공지사항을 가져오는 함수
def get_latest_notice():
    global last_notice_id

    # Selenium 옵션 설정
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    # 🔥 Chrome 브라우저 실행 파일 경로 (정확하게 확인해서 입력하세요!)
    options.binary_location = "D:\chromedriver\chrome\chrome.exe"

    # 🔥 ChromeDriver 경로 (정확한 위치로 수정)
    service = Service(executable_path="D:/chromedriver/chromedriver.exe")

    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = "https://mabinogimobile.nexon.com/News/Notice"
        driver.get(url)
        time.sleep(2)  # 페이지 로딩 대기

        first_notice = driver.find_element(By.CSS_SELECTOR, "ul.list > li.item")
        notice_id = first_notice.get_attribute("data-threadid")

        if last_notice_id == notice_id:
            return None, None

        last_notice_id = notice_id

        title_element = first_notice.find_element(By.CSS_SELECTOR, "a.title span")
        title = title_element.text.strip()
        link = f"https://mabinogimobile.nexon.com/News/Notice/View/{notice_id}"

        print(f"✅ 최신 공지 제목: {title}")
        print(f"🔗 링크: {link}")

        return title, link

    finally:
        driver.quit()

# 디스코드 클라이언트 설정
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# 봇이 시작될 때 실행
@client.event
async def on_ready():
    print(f"✅ 로그인 완료: {client.user}")
    check_notice.start()  # 공지사항 확인 루프 시작

# 공지사항 주기적으로 확인
@tasks.loop(seconds=60)
async def check_notice():
    title, link = get_latest_notice()
    if title and link:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(f"📢 **새 공지사항이 등록되었습니다!**\n**{title}**\n🔗 {link}")

# 디스코드 봇 실행
client.run(TOKEN)
