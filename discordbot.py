import os
import discord
import time
from discord.ext import tasks
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller

# 환경 변수에서 디스코드 토큰 및 채널 ID 불러오기
TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))

# 가장 최근에 전송한 공지사항 ID 저장 변수
last_notice_id = None

# 공지사항을 가져오는 함수
def get_latest_notice():
    global last_notice_id

    # 크롬드라이버 자동 설치
    chromedriver_autoinstaller.install()

    # Chrome 옵션 설정
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(options=options)

    try:
        url = "https://mabinogimobile.nexon.com/News/Notice"
        driver.get(url)
        time.sleep(2)

        first_notice = driver.find_element(By.CSS_SELECTOR, "ul.list > li.item")
        notice_id = first_notice.get_attribute("data-threadid")

        if last_notice_id == notice_id:
            return None, None  # 이미 전송한 공지

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

# 봇이 준비되었을 때 실행
@client.event
async def on_ready():
    print(f"✅ 로그인 완료: {client.user}")
    check_notice.start()

# 일정 시간마다 공지사항 확인
@tasks.loop(seconds=60)
async def check_notice():
    title, link = get_latest_notice()
    if title and link:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(f"📢 **새 공지사항이 등록되었습니다!**\n**{title}**\n🔗 {link}")

# 디스코드 봇 실행
client.run(TOKEN)
