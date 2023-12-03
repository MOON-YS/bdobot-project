from cmath import log
from distutils.sysconfig import PREFIX
import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import Button, View
#from dotenv import load_dotenv
#load_dotenv()
import time as tp
import datetime
import pandas as pd
import pymysql
from pymysql.constants import CLIENT
import os
import requests
from bs4 import BeautifulSoup
PREFIX = os.environ['PREFIX']
TOKEN = os.environ['TOKEN']

SQL_HOST = os.environ['SQL_HOST']
SQL_PORT = int(os.environ['SQL_PORT'])
SQL_USER = os.environ['SQL_USER']
SQL_PSWD = os.environ['SQL_PSWD']
      
KST = datetime.timezone(datetime.timedelta(hours=9))

conn = None
cur = None
str_on = "ON"
str_off = "OFF"
sql=""

conn = pymysql.connect(host=SQL_HOST,port=SQL_PORT, user=SQL_USER, password=SQL_PSWD, db='pythonDB',charset='utf8',client_flag = CLIENT.MULTI_STATEMENTS)
cur = conn.cursor()

today_week = datetime.datetime.now().weekday()
boss_time_data = pd.read_csv("./boss_alarm_schedule.csv",encoding="cp949")
bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())
def initGuild(search):
  global conn, cur
  updateTime = datetime.datetime.now(tz=KST).date()
  headers = {
      "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
      "Host":"www.kr.playblackdesert.com",
      "Accept-Encoding":"gzip, deflate, br",
      "Accept-Language":"ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"
    }

  url = f"https://www.kr.playblackdesert.com/ko-KR/Adventure/Guild/GuildProfile?guildName={search}&region=KR"
  try:
    res = requests.get(url, headers=headers) 
  except:
    print("잘못된 URL")
    return
  #res.raise_for_status()
  soup = BeautifulSoup(res.text, "html.parser")
  m = int(soup.select_one(".profile_detail > ul:nth-child(2) > li:nth-child(3) > span:nth-child(2) > span:nth-child(1) > em:nth-child(1)").text)
  if m == 0 :
    print("Error")
    return
  
  guildMaster = soup.select_one("span.text:nth-child(1) > a:nth-child(1)").text
  guild_members = []
  for tag in soup.find_all("span","text"):
      nm = str(tag.text.replace("\n",""))
      sql =f"INSERT IGNORE INTO UserData (UserName,Guild) VALUES('{nm}','{search}');"
      cur.execute(sql)
      guild_members.append(nm)
  guild_members = sorted(list(set(guild_members)))
  members_str = ';'.join(guild_members)
  
  sql =f"INSERT IGNORE INTO GuildData (upCounter,Num,GuildName,GuildMaster,Members) VALUES(72,{m},'{search}','{guildMaster}','{members_str}');"
  cur.execute(sql)
  conn.commit()
  
  for user in guild_members:
    
    sql =f"SELECT Guild FROM UserData WHERE UserName = '{user}'"
    cur.execute(sql)
    result = cur.fetchall()[0][0]
    if result != search:
      sql = f"""
        SELECT Logs FROM UserData WHERE UserName = '{user}';
        """
      cur.execute(sql)
      result = cur.fetchall()[0][0]
      userLog = ''
      if result != 'None':
        userLog = result.split(';')
        userLog.append(str(f"[{updateTime}] {search} 가입"))
        userLog = ';'.join(userLog)
      else:
        userLog = f"[{updateTime}] {search} 가입"
    
    conn.commit()
@bot.event
async def on_ready():
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")    
        alert_boss.start()
        update_db_conn.start()
        updateGuildMembers.start()
        print(f"Bot is Up and Ready! ::::     {datetime.datetime.now()}")
    except Exception as e:
        print(e)

class minSelect(discord.ui.View):
    answer1 = None
    kzk = None
    nbr = None
    kt = None
    krd = None
    gmt = None
    bll = None
    orc = None
    opn = None
    ds = None
    oi = None
    @discord.ui.select(
        placeholder="알람 시각을 설정하세요",
        options=[
            discord.SelectOption(label="소환시", value=0),
            discord.SelectOption(label="5분 전", value=5),
            discord.SelectOption(label="10분 전", value=10),
            discord.SelectOption(label="15분 전", value=15)
        ]
    )
    async def select_time(self, interaction: discord.interactions, select_item : discord.ui.Select):
        self.oi = interaction
        self.answer1 = select_item.values[0]
        self.children[0].disabled = True
        global sql, conn, cur
        
        sql = f"SELECT BS_KZK_{self.answer1}, BS_NBR_{self.answer1},BS_KT_{self.answer1},BS_KRD_{self.answer1},BS_GMT_{self.answer1},BS_BLL_{self.answer1},BS_ORC_{self.answer1},BS_OPN_{self.answer1},BS_DS_{self.answer1} FROM userTable WHERE id = {str(interaction.user.id)}"
        cur.execute(sql)
        result = cur.fetchall()[0]
        self.kzk = result[0]
        self.nbr = result[1]
        self.kt = result[2]
        self.krd = result[3]
        self.gmt = result[4]
        self.bll = result[5]
        self.orc = result[6]
        self.opn = result[7]
        self.ds = result[8]
        
        #크자카 버튼
        button_kzk = Button(label="크자카", style=(discord.ButtonStyle.blurple if self.kzk==1 else discord.ButtonStyle.gray))
        async def button_callback_kzk(interaction):
            global sql, conn, cur
            self.kzk = int(not self.kzk)
            self.children[1].style =(discord.ButtonStyle.blurple if self.kzk==1 else discord.ButtonStyle.gray)
            await interaction.response.edit_message(view=self)
        button_kzk.callback = button_callback_kzk
        self.add_item(button_kzk)
        
        #누베르 버튼
        button_nbr = Button(label="누베르", style=(discord.ButtonStyle.blurple if self.nbr==1 else discord.ButtonStyle.gray))
        async def button_callback_nbr(interaction):
            global sql, conn, cur
            self.nbr = int(not self.nbr)
            self.children[2].style =(discord.ButtonStyle.blurple if self.nbr==1 else discord.ButtonStyle.gray)
            await interaction.response.edit_message(view=self)
        button_nbr.callback = button_callback_nbr
        self.add_item(button_nbr)
        
        #쿠툼 버튼
        button_kt = Button(label="쿠툼", style=(discord.ButtonStyle.blurple if self.kt==1 else discord.ButtonStyle.gray))
        async def button_callback_kt(interaction):
            global sql, conn, cur
            self.kt = int(not self.kt)
            self.children[3].style =(discord.ButtonStyle.blurple if self.kt==1 else discord.ButtonStyle.gray)
            await interaction.response.edit_message(view=self)
        button_kt.callback = button_callback_kt
        self.add_item(button_kt)
        
        #카란다 버튼
        button_krd = Button(label="카란다", style=(discord.ButtonStyle.blurple if self.krd==1 else discord.ButtonStyle.gray))
        async def button_callback_krd(interaction):
            global sql, conn, cur
            self.krd = int(not self.krd)
            self.children[4].style =(discord.ButtonStyle.blurple if self.krd==1 else discord.ButtonStyle.gray)
            await interaction.response.edit_message(view=self)
        button_krd.callback = button_callback_krd
        self.add_item(button_krd)
        
        #가모스 버튼
        button_gmt = Button(label="가모스", style=(discord.ButtonStyle.blurple if self.gmt==1 else discord.ButtonStyle.gray))
        async def button_callback_gmt(interaction):
            global sql, conn, cur
            self.gmt = int(not self.gmt)
            self.children[5].style =(discord.ButtonStyle.blurple if self.gmt==1 else discord.ButtonStyle.gray)
            await interaction.response.edit_message(view=self)
        button_gmt.callback = button_callback_gmt
        self.add_item(button_gmt)
        
        #벨 버튼
        button_bll = Button(label="벨", style=discord.ButtonStyle.blurple if self.bll==1 else discord.ButtonStyle.gray)
        async def button_callback_bll(interaction):
            global sql, conn, cur
            self.bll = int(not self.bll)
            self.children[6].style =discord.ButtonStyle.blurple if self.bll==1 else discord.ButtonStyle.gray
            await interaction.response.edit_message(view=self)
        button_bll.callback = button_callback_bll
        self.add_item(button_bll)
        
        #귄트/무라카 버튼
        button_orc = Button(label="귄트/무라카", style=(discord.ButtonStyle.blurple if self.orc==1 else discord.ButtonStyle.gray))
        async def button_callback_orc(interaction):
            global sql, conn, cur
            self.orc = int(not self.orc)
            self.children[7].style =(discord.ButtonStyle.blurple if self.orc==1 else discord.ButtonStyle.gray)
            await interaction.response.edit_message(view=self)
        button_orc.callback = button_callback_orc
        self.add_item(button_orc)
        
        #오핀 버튼
        button_opn = Button(label="오핀", style=(discord.ButtonStyle.blurple if self.opn==1 else discord.ButtonStyle.gray))
        async def button_callback_opn(interaction):
            global sql, conn, cur
            self.opn = int(not self.opn)
            self.children[8].style =(discord.ButtonStyle.blurple if self.opn==1 else discord.ButtonStyle.gray)
            await interaction.response.edit_message(view=self)
        button_opn.callback = button_callback_opn
        self.add_item(button_opn)
        
        #검그 버튼
        button_ds = Button(label="검은그림자", style=(discord.ButtonStyle.blurple if self.ds==1 else discord.ButtonStyle.gray))
        async def button_callback_ds(interaction):
            global sql, conn, cur
            self.ds = int(not self.ds)
            self.children[9].style =(discord.ButtonStyle.blurple if self.ds==1 else discord.ButtonStyle.gray)
            await interaction.response.edit_message(view=self)
        button_ds.callback = button_callback_ds
        self.add_item(button_ds)
        
        #모두 선택 버튼
        button_all = Button(label="모두 선택", style=discord.ButtonStyle.green)
        async def button_callback_all(interaction):
            global sql, conn, cur
            self.kzk = 1
            self.nbr = 1
            self.kt = 1
            self.krd = 1
            self.gmt = 1
            self.bll = 1
            self.orc = 1
            self.opn = 1
            self.ds = 1
            for i in range(1,10):
                self.children[i].style =discord.ButtonStyle.blurple
            await interaction.response.edit_message(view=self)
        button_all.callback = button_callback_all
        self.add_item(button_all)
        
        #모두 해제 버튼
        button_alld = Button(label="모두 해제", style=discord.ButtonStyle.red)
        async def button_callback_alld(interaction):
            global sql, conn, cur
            self.kzk = 0
            self.nbr = 0
            self.kt = 0
            self.krd = 0
            self.gmt = 0
            self.bll = 0
            self.orc = 0
            self.opn = 0
            self.ds = 0
            for i in range(1,10):
                self.children[i].style =discord.ButtonStyle.gray
            await interaction.response.edit_message(view=self)
        button_alld.callback = button_callback_alld
        self.add_item(button_alld)
        
        #적용 버튼
        button_accept = Button(label="적용", style=discord.ButtonStyle.green)
        async def button_callback_accept(interaction):
            global sql, conn, cur
            sql = f"UPDATE userTable SET BS_KZK_{self.answer1} = {self.kzk}, BS_NBR_{self.answer1} = {self.nbr}, BS_KT_{self.answer1} = {self.kt}, BS_KRD_{self.answer1} = {self.krd}, BS_GMT_{self.answer1} = {self.gmt}, BS_BLL_{self.answer1} = {self.bll}, BS_ORC_{self.answer1} = {self.orc}, BS_OPN_{self.answer1} = {self.opn}, BS_DS_{self.answer1} = {self.ds} WHERE id = {str(interaction.user.id)}"
            cur.execute(sql)
            conn.commit()
            await interaction.response.send_message(f"알람이 적용되었습니다", delete_after=5,ephemeral=True)
            await self.oi.delete_original_response()
        button_accept.callback = button_callback_accept
        self.add_item(button_accept)
        
        #취소 버튼
        button_cancle = Button(label="취소", style=discord.ButtonStyle.red)
        async def button_callback_cancle(interaction):
            await interaction.response.send_message(f"알람 설정이 취소되었습니다", delete_after=5,ephemeral=True)
            await self.oi.delete_original_response()
        button_cancle.callback = button_callback_cancle
        self.add_item(button_cancle)
    
        await interaction.response.edit_message(view=self)
  
#월드 보스 알람 설정
@bot.tree.command(name="월드보스_알람설정", description="보스 알람을 설정합니다.")
async def 월드보스_알람설정(interaction: discord.interactions):
    global cur, conn
    sql = f"INSERT IGNORE INTO userTable (id, BS_NBR_0, BS_NBR_5 , BS_NBR_10, BS_NBR_15, BS_KZK_0, BS_KZK_5  , BS_KZK_10 , BS_KZK_15 ,BS_KRD_0 , BS_KRD_5 , BS_KRD_10 , BS_KRD_15 ,BS_KT_0 , BS_KT_5 , BS_KT_10 , BS_KT_15 ,BS_OPN_0 , BS_OPN_5 , BS_OPN_10 , BS_OPN_15 ,BS_GMT_0 , BS_GMT_5 , BS_GMT_10 , BS_GMT_15 ,BS_BLL_0 , BS_BLL_5 , BS_BLL_10 , BS_BLL_15 ,BS_ORC_0 , BS_ORC_5 ,BS_ORC_10 ,BS_ORC_15, BS_DS_0, BS_DS_5  , BS_DS_10 , BS_DS_15, BS_MUD_ALRM,BS_MUD_RPRT,BS_BEG_ALRM,BS_BEG_RPRT,BS_RAU_ALRM,BS_RAU_RPRT)VALUES({str(int(interaction.user.id))},1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1,0)"
    cur.execute(sql)
    conn.commit()
    view = minSelect()
    await interaction.response.send_message(f"{interaction.user.mention} 보스알람을 설정합니다. \n기본설정은 모두 ON 입니다. \n해당 메세지는 2분후 자동으로 삭제됩니다",view=view, delete_after=120, ephemeral=True)

#월드 보스 알람 현황 
@bot.tree.command(name="월드보스_알람현황", description="알람 등록 현황을 출력합니다")
async def 월드보스_알람현황(interaction: discord.interactions):
    global cur, conn
    sql = f"INSERT IGNORE INTO userTable (id, BS_NBR_0, BS_NBR_5 , BS_NBR_10, BS_NBR_15, BS_KZK_0, BS_KZK_5  , BS_KZK_10 , BS_KZK_15 ,BS_KRD_0 , BS_KRD_5 , BS_KRD_10 , BS_KRD_15 ,BS_KT_0 , BS_KT_5 , BS_KT_10 , BS_KT_15 ,BS_OPN_0 , BS_OPN_5 , BS_OPN_10 , BS_OPN_15 ,BS_GMT_0 , BS_GMT_5 , BS_GMT_10 , BS_GMT_15 ,BS_BLL_0 , BS_BLL_5 , BS_BLL_10 , BS_BLL_15 ,BS_ORC_0 , BS_ORC_5 ,BS_ORC_10 ,BS_ORC_15, BS_DS_0, BS_DS_5  , BS_DS_10 , BS_DS_15, BS_MUD_ALRM,BS_MUD_RPRT,BS_BEG_ALRM,BS_BEG_RPRT,BS_RAU_ALRM,BS_RAU_RPRT)VALUES({str(int(interaction.user.id))},1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1,0)"
    cur.execute(sql)
    conn.commit()
    num = [0,5,10,15]
    nm = ['크자카','누베르','쿠툼','카란다','가모스', '벨', '귄트/무라카', '오핀', '검은그림자']
    s = [""]
    for i in num:
        sql = f"SELECT BS_KZK_{i}, BS_NBR_{i},BS_KT_{i},BS_KRD_{i},BS_GMT_{i},BS_BLL_{i},BS_ORC_{i},BS_OPN_{i},BS_DS_{i} FROM userTable WHERE id = {str(interaction.user.id)}"
        cur.execute(sql)
        result = cur.fetchall()[0]
        for t in range(0, len(result)):
            if result[t] == 1 :
                s.append(f'[{i}분]{nm[t]}' if i != 0 else f"[즉시]{nm[t]}")
        s.append('\n')
    d = '```css'+'\n'.join(s)+'```'
    embed = discord.Embed(
        color=discord.Colour.dark_blue(),
        description=d
    )
    await interaction.response.send_message(f"등록 현황을 표시합니다",ephemeral=True,embed=embed)

#필드보스 알람 시행(1회)
@tasks.loop(count=1)
async def fieldBossSend(boss_nm):
    global cur
    sql = f"SELECT id FROM userTable WHERE BS_{boss_nm}_ALRM= 1"
    cur.execute(sql)
    result = cur.fetchall()
    dic =  {'BEG':'베그','MUD':'진흙','RAU':'라우라우'}
    
    for record in result:
        user = await bot.fetch_user(int(record[0]))
        msg = f"'{dic[boss_nm]}'가 소환 되었습니다!"
        await user.send(msg)
    
#필드보스 제보 및 알람
#필보 제보 버튼
class fbRprt(discord.ui.View):
    def __init__(self, is_beg_reported, is_mud_reported, is_rau_reported,beg_stack,mud_stack,rau_stack, oi):
        super().__init__()
        self.is_beg_reported = is_beg_reported
        self.is_mud_reported = is_mud_reported
        self.is_rau_reported = is_rau_reported
        self.beg_stack = beg_stack
        self.mud_stack = mud_stack
        self.rau_stack = rau_stack
        self.oi = oi
        
    @discord.ui.button(label="베그",style=discord.ButtonStyle.red)
    async def beg_click(self, interaction: discord.Interaction, button:discord.ui.Button):
        global cur, conn
        boss_nm = 'BEG'
        sql = f"""
        SELECT ZEN_TIME_HH, ZEN_TIME_MM FROM fieldBoss WHERE BOSS_NM='{boss_nm}'
        """
        cur.execute(sql)
        result = cur.fetchall()[0]
        last_zen_hh = result()[0]
        last_zen_mm = result()[1]
        current = 60*int(datetime.datetime.now(tz=KST).hour)+int(datetime.datetime.now(tz=KST).minute)
        zen = 60*(last_zen_hh+12) + last_zen_mm
        if current < zen:
            await interaction.response.send_message("젠타임이 아닙니다", ephemeral=True,delete_after=5)
            
        elif self.is_beg_reported == 1 :
            await interaction.response.send_message("이미 제보하셨습니다.", ephemeral=True,delete_after=5)
        #제보스택 9 이상 달성시 수행
        elif self.beg_stack >= 9:
            fieldBossSend.start(boss_nm)
            sql = f"""
            UPDATE fieldBoss SET REPORT_STACK = 0 WHERE BOSS_NM = {boss_nm};
            UPDATE userTable SET BS_{boss_nm}_RPRT = 0;
            """
            cur.execute(sql)
            conn.commit()
            
        else:
            hh = int(datetime.datetime.now(tz=KST).hour)
            mm = int(datetime.datetime.now(tz=KST).minute)
            sql = f"""
            UPDATE userTable SET BS_{boss_nm}_RPRT = 1 WHERE id = {str(interaction.user.id)};
            UPDATE fieldBoss SET REPORT_STACK = REPORT_STACK +1 WHERE BOSS_NM = {boss_nm};
            UPDATE fieldBoss SET ZEN_TIME_HH = {hh} WHERE BOSS_NM = {boss_nm};
            UPDATE fieldBoss SET ZEN_TIME_MM = {mm} WHERE BOSS_NM = {boss_nm};
            """
            cur.execute(sql)
            conn.commit()

            await interaction.response.send_message("베그 제보 완료", ephemeral=True,delete_after=5)
        await self.oi.delete_original_response()
            
    @discord.ui.button(label="진흙",style=discord.ButtonStyle.red)
    async def mud_click(self, interaction: discord.Interaction, button:discord.ui.Button):
        boss_nm = "MUD"
        global cur, conn
        sql = f"""
        SELECT ZEN_TIME_HH, ZEN_TIME_MM FROM fieldBoss WHERE BOSS_NM='{boss_nm}';
        """
        cur.execute(sql)
        result = cur.fetchall()[0]
        last_zen_hh = result()[0]
        last_zen_mm = result()[1]
        current = 60*int(datetime.datetime.now(tz=KST).hour)+int(datetime.datetime.now(tz=KST).minute)
        zen = 60*(last_zen_hh+12) + last_zen_mm
        if current < zen:
            await interaction.response.send_message("젠타임이 아닙니다", ephemeral=True,delete_after=5)
            
        elif self.is_beg_reported == 1 :
            await interaction.response.send_message("이미 제보하셨습니다.", ephemeral=True,delete_after=5)
        #제보스택 9 이상 달성시 수행
        elif self.beg_stack >= 9:
            fieldBossSend.start(boss_nm)
            sql = f"""
            UPDATE fieldBoss SET REPORT_STACK = 0 WHERE BOSS_NM = {boss_nm};
            UPDATE userTable SET BS_{boss_nm}_RPRT = 0;
            """
            cur.execute(sql)
            conn.commit()
            
        else:
            hh = int(datetime.datetime.now(tz=KST).hour)
            mm = int(datetime.datetime.now(tz=KST).minute)
            sql = f"""
            UPDATE userTable SET BS_{boss_nm}_RPRT = 1 WHERE id = {str(interaction.user.id)};
            UPDATE fieldBoss SET REPORT_STACK = REPORT_STACK +1 WHERE BOSS_NM = {boss_nm};
            UPDATE fieldBoss SET ZEN_TIME_HH = {hh} WHERE BOSS_NM = {boss_nm};
            UPDATE fieldBoss SET ZEN_TIME_MM = {mm} WHERE BOSS_NM = {boss_nm};
            """
            cur.execute(sql)
            conn.commit()

            await interaction.response.send_message("진흙 제보 완료", ephemeral=True,delete_after=5)
        await self.oi.delete_original_response()
  
    @discord.ui.button(label="라우",style=discord.ButtonStyle.red)
    async def rau_click(self, interaction: discord.Interaction, button:discord.ui.Button):
        global cur, conn
        boss_nm = "RAU"
        sql = f"""
        SELECT ZEN_TIME_HH, ZEN_TIME_MM FROM fieldBoss WHERE BOSS_NM='{boss_nm}';
        """
        cur.execute(sql)
        result = cur.fetchall()[0]
        last_zen_hh = result()[0]
        last_zen_mm = result()[1]
        current = 60*int(datetime.datetime.now(tz=KST).hour)+int(datetime.datetime.now(tz=KST).minute)
        zen = 60*(last_zen_hh+12) + last_zen_mm
        #젠타임 외 제보시 거부
        if current < zen:
            await interaction.response.send_message("젠타임이 아닙니다", ephemeral=True,delete_after=5)
        #중복 제보 방지
        elif self.is_beg_reported == 1 :
            await interaction.response.send_message("이미 제보하셨습니다.", ephemeral=True,delete_after=5)
        #제보스택 9 이상 달성시 수행
        elif self.beg_stack >= 9:
            fieldBossSend.start(boss_nm)
            hh = int(datetime.datetime.now(tz=KST).hour)
            mm = int(datetime.datetime.now(tz=KST).minute)
            sql = f"""
            UPDATE fieldBoss SET REPORT_STACK = 0 WHERE BOSS_NM = {boss_nm};
            UPDATE userTable SET BS_{boss_nm}_RPRT = 0;
            UPDATE fieldBoss SET ZEN_TIME_HH = {hh} WHERE BOSS_NM = {boss_nm};
            UPDATE fieldBoss SET ZEN_TIME_MM = {mm} WHERE BOSS_NM = {boss_nm};
            """
            cur.execute(sql)
            conn.commit()
        #그외 제보 스택 추가
        else:
            sql = f"""
            UPDATE userTable SET BS_{boss_nm}_RPRT = 1 WHERE id = {str(interaction.user.id)};
            UPDATE fieldBoss SET REPORT_STACK = REPORT_STACK +1 WHERE BOSS_NM = {boss_nm};
            """
            cur.execute(sql)
            conn.commit()

            await interaction.response.send_message("라우라우 제보 완료", ephemeral=True,delete_after=5)
        await self.oi.delete_original_response()
     
#필보 제보 명령
@bot.tree.command(name="필드보스_제보", description="필드 보스 스폰을 DB에 제보합니다")
async def 필드보스_제보(interaction: discord.interactions):
    global cur, conn
    sql = f"INSERT IGNORE INTO userTable (id, BS_NBR_0, BS_NBR_5 , BS_NBR_10, BS_NBR_15, BS_KZK_0, BS_KZK_5  , BS_KZK_10 , BS_KZK_15 ,BS_KRD_0 , BS_KRD_5 , BS_KRD_10 , BS_KRD_15 ,BS_KT_0 , BS_KT_5 , BS_KT_10 , BS_KT_15 ,BS_OPN_0 , BS_OPN_5 , BS_OPN_10 , BS_OPN_15 ,BS_GMT_0 , BS_GMT_5 , BS_GMT_10 , BS_GMT_15 ,BS_BLL_0 , BS_BLL_5 , BS_BLL_10 , BS_BLL_15 ,BS_ORC_0 , BS_ORC_5 ,BS_ORC_10 ,BS_ORC_15, BS_DS_0, BS_DS_5  , BS_DS_10 , BS_DS_15, BS_MUD_ALRM,BS_MUD_RPRT,BS_BEG_ALRM,BS_BEG_RPRT,BS_RAU_ALRM,BS_RAU_RPRT)VALUES({str(int(interaction.user.id))},1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1,0)"
    cur.execute(sql)
    conn.commit()
    
    sql = f"SELECT BS_BEG_RPRT, BS_MUD_RPRT, BS_RAU_RPRT FROM userTable WHERE id = {str(interaction.user.id)}"
    cur.execute(sql)
    result = cur.fetchall()[0]
    sql = 'SELECT REPORT_STACK FROM fieldBoss'
    cur.execute(sql)
    result2 = cur.fetchall()
    result = result + (result2[0][0],result2[1][0],result2[2][0])
    view = fbRprt(result[0],result[1],result[2],result[3],result[4],result[5],interaction)
    
    await interaction.response.send_message(f"제보 감사합니다.",ephemeral=True, view=view)

#필드보스 시간표
@bot.tree.command(name="필드보스_시간표", description="필드 보스 스폰 시간을 확인합니다")
async def 필드보스_시간표(interaction: discord.interactions):
    global cur
    boss_cd = ('BEG','MUD','RAU')
    boss_nm = {'BEG':'베그','MUD':'진흙','RAU':'라우'}
    s=[""]
    for code in boss_cd:
        sql = f"""
        SELECT ZEN_TIME_HH, ZEN_TIME_MM FROM fieldBoss WHERE BOSS_NM='{code}'
        """
        cur.execute(sql)
        tmp = cur.fetchall()[0]
        lzen_hh = tmp[0]
        lzen_mm = tmp[1] 
        s.append(f"<{boss_nm[code]}> [{str(lzen_hh+12).zfill(2) if lzen_hh+12<24 else str(lzen_hh+12-24).zfill(2)}:{str(lzen_mm).zfill(2)}] ~ [{str(lzen_hh+19).zfill(2) if lzen_hh+19<24 else str(lzen_hh+19-24).zfill(2)}:{str(lzen_mm).zfill(2)}]")
    d = '```xml'+'\n'.join(s)+'```'
    
    embed = discord.Embed(
        title="필드 보스 젠 시간표",
        color=discord.Colour.dark_red(),
        description=d
    )
    await interaction.response.send_message(ephemeral=True,embed=embed)
    
#필보 알람 버튼
class fbAlarm(discord.ui.View):
    def __init__(self, beg, mud, rau, oi):
        super().__init__()
        self.mud = mud
        self.beg = beg
        self.rau = rau
        self.children[0].style =(discord.ButtonStyle.blurple if self.beg==1 else discord.ButtonStyle.gray)
        self.children[1].style =(discord.ButtonStyle.blurple if self.mud==1 else discord.ButtonStyle.gray)
        self.children[2].style =(discord.ButtonStyle.blurple if self.rau==1 else discord.ButtonStyle.gray)
        self.oi = oi

    @discord.ui.button(label="베그",style=discord.ButtonStyle.blurple)
    async def beg_click(self, interaction: discord.Interaction, button:discord.ui.Button):
        self.beg = int(not self.beg)
        self.children[0].style =(discord.ButtonStyle.blurple if self.beg==1 else discord.ButtonStyle.gray)
        await interaction.response.edit_message(view=self)
            
    @discord.ui.button(label="진흙",style=discord.ButtonStyle.blurple)
    async def mud_click(self, interaction: discord.Interaction, button:discord.ui.Button):
        self.mud = int(not self.mud)
        self.children[1].style =(discord.ButtonStyle.blurple if self.mud==1 else discord.ButtonStyle.gray)
        await interaction.response.edit_message(view=self)
  
    @discord.ui.button(label="라우",style=discord.ButtonStyle.blurple)
    async def rau_click(self, interaction: discord.Interaction, button:discord.ui.Button):
        self.rau = int(not self.rau)
        self.children[2].style =(discord.ButtonStyle.blurple if self.rau==1 else discord.ButtonStyle.gray)
        await interaction.response.edit_message(view=self)
        
    @discord.ui.button(label="적용",style=discord.ButtonStyle.green)
    async def accept_click(self, interaction: discord.Interaction, button:discord.ui.Button):
        global sql, cur, conn
        sql = f"UPDATE userTable SET BS_BEG_ALRM = {self.beg}, BS_MUD_ALRM = {self.mud},BS_RAU_ALRM = {self.rau} WHERE id = {str(interaction.user.id)}"
        cur.execute(sql)
        conn.commit()
        await interaction.response.send_message(f"알람이 적용되었습니다", delete_after=5,ephemeral=True)
        await self.oi.delete_original_response()
        
    @discord.ui.button(label="취소",style=discord.ButtonStyle.green)
    async def cancle_click(self, interaction: discord.Interaction, button:discord.ui.Button):
        await interaction.response.send_message(f"알람이 취소되었습니다", delete_after=5,ephemeral=True)
        await self.oi.delete_original_response()

#필보 알람 명령
@bot.tree.command(name="필드보스_알람", description="필드보스 알람을 설정하거나 젠타임을 확인합니다")
async def 필드보스_알람(interaction: discord.interactions):
    
    sql = f"INSERT IGNORE INTO userTable (id, BS_NBR_0, BS_NBR_5 , BS_NBR_10, BS_NBR_15, BS_KZK_0, BS_KZK_5  , BS_KZK_10 , BS_KZK_15 ,BS_KRD_0 , BS_KRD_5 , BS_KRD_10 , BS_KRD_15 ,BS_KT_0 , BS_KT_5 , BS_KT_10 , BS_KT_15 ,BS_OPN_0 , BS_OPN_5 , BS_OPN_10 , BS_OPN_15 ,BS_GMT_0 , BS_GMT_5 , BS_GMT_10 , BS_GMT_15 ,BS_BLL_0 , BS_BLL_5 , BS_BLL_10 , BS_BLL_15 ,BS_ORC_0 , BS_ORC_5 ,BS_ORC_10 ,BS_ORC_15, BS_DS_0, BS_DS_5  , BS_DS_10 , BS_DS_15, BS_MUD_ALRM,BS_MUD_RPRT,BS_BEG_ALRM,BS_BEG_RPRT,BS_RAU_ALRM,BS_RAU_RPRT)VALUES({str(int(interaction.user.id))},1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1,0)"
    cur.execute(sql)
    conn.commit()

    sql = f"SELECT BS_BEG_ALRM, BS_MUD_ALRM, BS_RAU_ALRM FROM userTable WHERE id = {str(interaction.user.id)};"
    cur.execute(sql)
    result = cur.fetchall()[0]
    view = fbAlarm(result[0],result[1],result[2],interaction)
    
    await interaction.response.send_message(f"필드보스 알람을 설정합니다",delete_after=60,ephemeral=True ,view=view)

#길드멤버 보기
@bot.tree.command(name="길드정보", description="길드 현원을 불러옵니다")
async def 길드정보(interaction: discord.interactions, 길드명:str):
    sql =f"SELECT Members,GuildMaster,Num FROM GuildData WHERE GuildName = '{길드명}'"
    cur.execute(sql)
    result = cur.fetchall()
    if len(result) == 0:
        await interaction.response.send_message(f"존재하지 않는 길드이거나 추적되지 않은 길드입니다. 잠시후 시도해주세요")
        initGuild(길드명)
        return
    result = result[0]
    members = result[0]
    gm = result[1]
    membersNum = int(result[2])
    members = members.split(';')
    l = len(members)
    p = round(l / 3)
    embed=discord.Embed(title=f"{길드명}")
    embed.add_field(name = f"길드대장 : {gm}", value = "",inline=False)
    embed.add_field(name = f"현원 : {membersNum}", value="", inline=False)
    
    m1 = '\n'.join(members[:p])
    m2 = '\n'.join(members[p:p*2])
    m3 = '\n'.join(members[p*2:])
    
    embed.add_field(name = "", value=m1,inline=True)
    embed.add_field(name = "", value=m2,inline=True)
    embed.add_field(name = "", value=m3,inline=True)
    embed.set_footer(text="DB Since 2023.12.07")
    await interaction.response.send_message(embed=embed)
    
#길드 연혁 보기
@bot.tree.command(name="길드연혁", description="길드 연혁을 불러옵니다")
async def 길드연혁(interaction: discord.interactions, 길드명:str):
    sql =f"SELECT Logs FROM GuildData WHERE GuildName = '{길드명}'"
    cur.execute(sql)
    result = cur.fetchall()
    if len(result) == 0: 
        await interaction.response.send_message(f"존재하지 않는 길드이거나 추적되지 않은 길드입니다. 잠시후 시도해주세요")
        initGuild(길드명)
        return
    
    result = result[0][0]
    logs = result.split(';')
    log_str="\n".join(logs)
    embed=discord.Embed(title=f"{길드명} 길드연혁")
    embed.add_field(name = "", value=log_str,inline=True)
    embed.set_footer(text="DB Since 2023.12.07")
    await interaction.response.send_message(embed=embed)

#유저추적
@bot.tree.command(name="길드추적", description="해당유저의 길드가입연혁 및 현재 길드를 불러옵니다")
async def 길드추적(interaction: discord.interactions, 가문명:str):
  sql =f"SELECT Guild, Logs FROM UserData WHERE UserName = '{가문명}'"
  cur.execute(sql)
  result = cur.fetchall()
  if len(result) == 0: return
  guild = result[0][0]
  result = result[0][1]
  logs = result.split(';')
  log_str="\n".join(logs)
  embed=discord.Embed(title=f"가문명 : {가문명}")
  embed.add_field(name = f"현재길드 : {guild}", value = "",inline=False)
  embed.add_field(name = f"가입연혁", value = f"{log_str}",inline=False)
  embed.set_footer(text="DB Since 2023.12.07")
  await interaction.response.send_message(embed=embed)
  
#월드보스 알람 시행(매분마다 체크)
@tasks.loop(seconds=60)
async def alert_boss():
    global boss_time_data,sql,cur,conn,bot
    today_week = datetime.datetime.now(tz=KST).weekday()
    crt_hh = int(datetime.datetime.now(tz=KST).hour)
    crt_mm = int(datetime.datetime.now(tz=KST).minute)
    
    now_alarm = boss_time_data[(boss_time_data["DATE_CODE"]==today_week)&(boss_time_data["HH"]==crt_hh)&(boss_time_data["mm"]==crt_mm)]
    if(now_alarm["DATE"].count() == 1):
        current_boss1 = now_alarm["BOSS_NM1"].values[0]
        current_boss2 = now_alarm["BOSS_NM2"].values[0]
        current_boss1_code = now_alarm["DB_CODE1"].values[0]
        current_boss2_code = now_alarm["DB_CODE2"].values[0]
        time_tt = now_alarm["TIME"].values[0]
        
        if not current_boss2 == ".":
            sql = f"SELECT id FROM userTable WHERE {current_boss1_code}=1 OR {current_boss2_code}=1"
        else:
            sql = f"SELECT id FROM userTable WHERE {current_boss1_code}=1"

        cur.execute(sql)
        result = cur.fetchall()
        print(str(datetime.datetime.now(tz=KST).date())+"Send to "+str(len(result)) +" Player")
        for record in result:
            user = await bot.fetch_user(int(record[0]))
            msg = f" {current_boss1}{ ('/'+ current_boss2) if not current_boss2=='.' else ''} 출현{(' '+str(time_tt)+'분 전') if not time_tt==0 else '!'}"
            await user.send(msg)
    tp.sleep(1)
    
#DB 재연결
@tasks.loop(hours=4)
async def update_db_conn():
    global conn, cur
    
    conn.commit()
    conn.close()
    conn = pymysql.connect(host=SQL_HOST,port=SQL_PORT, user=SQL_USER, password=SQL_PSWD, db='pythonDB',charset='utf8',client_flag = CLIENT.MULTI_STATEMENTS)
    cur = conn.cursor()
    now = datetime.datetime.now(tz=KST).date()

    print(f"{now} :::: DB connection updated")
    
    tp.sleep(1)

@tasks.loop(minutes=20)
async def updateGuildMembers():
  updateTime = datetime.datetime.now(tz=KST).date()
  sql =f"SELECT GuildName,upCounter FROM GuildData"
  cur.execute(sql)
  result = cur.fetchall()
  for search,upCounter in result:
    sql = f"""
    SELECT upCounter FROM GuildData WHERE GuildName = "{search}";
    """
    cur.execute(sql)
    result = cur.fetchall()[0]
    upCounter = int(result[0]) - 1
    
    if upCounter == 0:
      headers = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Host":"www.kr.playblackdesert.com",
        "Accept-Encoding":"gzip, deflate, br",
        "Accept-Language":"ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"
      }

      url = f"https://www.kr.playblackdesert.com/ko-KR/Adventure/Guild/GuildProfile?guildName={search}&region=KR" 
      res = requests.get(url, headers=headers) 
      res.raise_for_status()
      

      sql = f"""
      SELECT Members,Logs FROM GuildData WHERE GuildName = "{search}";
      """
      cur.execute(sql)
      result = cur.fetchall()[0]
      
      prev_guild_member = result[0].split(';')
      log = result[1].split(';')
      log.remove('None')
      
      soup = BeautifulSoup(res.text, "html.parser")
      
      guild_members = []
      guildMaster = soup.select_one("span.text:nth-child(1) > a:nth-child(1)").text

      for tag in soup.find_all("span","text"):
        nm = str(tag.text.replace("\n",""))
        cur.execute(sql)
        guild_members.append(nm)

      guild_members = sorted(list(set(guild_members)))

      new = set(guild_members)
      old = set(prev_guild_member)
      
      addedmember = new - old #추가된인원
      secemember = old - new #나간 인원

      if len(addedmember) > 0:
        for aMember in addedmember:
          log.append(f"[{updateTime}] {aMember} 가입")

          sql = f"""
          INSERT IGNORE INTO UserData (UserName,Guild) VALUES('{aMember}','{search}');
          UPDATE UserData SET Guild = '{search}' WHERE UserName = '{aMember}';
          """
          cur.execute(sql)
          sql = f"""
          SELECT Logs FROM UserData WHERE UserName = '{aMember}';
          """
          cur.execute(sql)
          result = cur.fetchall()[0][0]
          userLog = ''
          if result != 'None':
            userLog = result.split(';')
            userLog.append(str(f"[{updateTime}] {search} 가입"))
            userLog = ';'.join(userLog)
          else:
            userLog = f"[{updateTime}] {search} 가입"
          
          sql = f"UPDATE UserData SET Logs = '{userLog}' WHERE UserName = '{aMember}'"
          cur.execute(sql)
          conn.commit()
          
      if len(secemember) > 0:
        for sMember in secemember:
          log.append(f"[{updateTime}] {sMember} 탈퇴")
          
          sql = f"""
          INSERT IGNORE INTO UserData (UserName,Guild) VALUES('{sMember}','{search}');
          UPDATE UserData SET Guild = 'None' WHERE UserName = '{sMember}';
          """
          cur.execute(sql)
          conn.commit()
          sql = f"""
          SELECT Logs FROM UserData WHERE UserName = "{sMember}";
          """
          cur.execute(sql)
          result = cur.fetchall()[0][0]
          if result != 'None':
            userLog = result.split(';')
            userLog.append(str(f"[{updateTime}] {search} 탈퇴"))
            userLog = ';'.join(userLog)
          else:
            userLog = f"[{updateTime}] {search} 탈퇴"
            
          sql = f"UPDATE UserData SET Logs = '{userLog}' WHERE UserName = '{sMember}'"
          cur.execute(sql)
          conn.commit()

      
      log_str = ';'.join(log[-50:])
      memberNum = len(guild_members)
      members_str = ';'.join(guild_members)
      
      
      sql = f"""
      UPDATE GuildData SET upCounter = 72 WHERE GuildName = '{search}';
      UPDATE GuildData SET GuildMaster = '{guildMaster}' WHERE GuildName = '{search}';
      UPDATE GuildData SET Num = {memberNum} WHERE GuildName = '{search}';
      UPDATE GuildData SET Members = '{members_str}' WHERE GuildName = '{search}';
      UPDATE GuildData SET Logs = '{log_str}' WHERE GuildName = '{search}';
      """
      cur.execute(sql)
      conn.commit()
    
    else :
      sql = f"""
      UPDATE GuildData SET upCounter = {upCounter} WHERE GuildName = "{search}";
      """
      cur.execute(sql)
      conn.commit()

try:
    bot.run(TOKEN)
except discord.errors.LoginFailure as e:
    print("Improper token has been passed.")
    
#월드보스 알람(완)
#필드보스 제보&알람(완) == 밴 기능 고려중

#카프라스 계산기
#크론석 계산기
#생산 거점 검색
#쿠폰 제보 & 열람
#대량가공알람 
#요리연금알람
#재배알람
#데키아 등불 효율 계산기
#명령어 및 봇 정보 일람
#연구소 패치
#이벤트
#보스시간표