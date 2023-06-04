import os, sys, shutil, traceback, time
import config

try:
  import telebot
  from telebot import types
  from PIL import Image
  import requests
  from mutagen.mp4 import MP4, MP4Cover
  from pytube import YouTube
except:
  os.system("pip install pyTelegramBotAPI Pillow requests mutagen pytube")
  sys.exit(os.system("python3 main.py"))

def check_link(link):
  try:
    link = "http" + link.split("http")[1]
    if link[:8] == "https://":
      http = "https://"
    elif link[:7] == "http://":
      http = "http://"
    if link.split(http)[1].split("/")[0] == "music.youtube.com" or link.split(
        http)[1].split("/")[0] == "youtube.com" or link.split(http)[1].split(
          "/")[0] == "www.youtube.com" or link.split(http)[1].split(
            "/")[0] == "m.youtube.com" or link.split(http)[1].split(
              "/")[0] == "youtu.be":
      return True
    else:
      return False
  except:
    return False


def youtube(ID):
  try:
    url = "https://m.youtube.com/watch?v=" + ID
    result = requests.get(url).text
    try:
      check_video = result.split('{"status":"')[1].split('",')[0]
      if check_video == "OK":
        try:
          title = result.split("<title>")[1].split("</title>")[0].replace(
            " - YouTube", "")
        except:
          title = "ERROR"
        try:
          author = result.split('"ownerChannelName":"')[1].split(
            '"')[0].replace(" - Topic", "")
        except:
          author = "ERROR"
        try:
          length = result.split('"lengthSeconds":"')[1].split('"')[0]
        except:
          length = "ERROR"
        return {
          "title": replace_forbidden_chars(title),
          "author": replace_forbidden_chars(author),
          "length": length
        }
      elif check_video == "ERROR":
        return -3
      else:
        return -4
    except:
      return -2
  except:
    return -1


def get_id(link):
  try:
    link = "http" + link.split("http")[1]
    if link[:8] == "https://":
      http = "https://"
      x = 17
    elif link[:7] == "http://":
      http = "http://"
      x = 16
    if link[:x] == http + "youtu.be/":
      return link.split(http + "youtu.be/")[1].split("&")[0]
    else:
      return link.split("/watch?v=")[1].split("&")[0]
  except:
    return ""


def add_audiotag(file, name, author, cover):
  try:
    audio = MP4(file)
    audio['\xa9nam'] = name
    audio["\xa9ART"] = author
    with open(cover, "rb") as f:
      cover_data = f.read()
    cover = MP4Cover(cover_data)
    audio['covr'] = [cover]
    audio.save()
    return True
  except:
    return False


def get_thumb(ID, dir):
  try:
    url = "https://i.ytimg.com/vi/" + ID + "/maxresdefault.jpg"
    thumb = requests.get(url).content
    with open(dir + "thumb.jpg", "wb") as f:
      f.write(thumb)
    image = Image.open(dir + "thumb.jpg")
    width, height = image.size
    size = min(width, height)
    x = (width - size) // 2
    y = (height - size) // 2
    cropped_image = image.crop((x, y, x + size, y + size))
    cropped_image.save(dir + "/thumb.jpg")
    return True
  except:
    return False

def is_user_subscribed(user_id):
  try:
    chat_member = bot.get_chat_member("@DimLuxBlog", user_id)
    return chat_member.status == "member" or chat_member.status == "creator"
  except:
    return False

def replace_forbidden_chars(filename):
  forbidden_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
  for char in forbidden_chars:
    filename = filename.replace(char, '-')
  return filename

def get_audio_from_video(ID, filename):
  try:
    try:
      YouTube("https://www.youtube.com/watch?v=" + ID).streams.filter(only_audio=True).first(
      ).download(output_path = "", filename = filename)
    except:
      os.system("pip install --upgrade pytube")
      YouTube("https://www.youtube.com/watch?v=" + ID).streams.filter(only_audio=True).first(
      ).download(output_path = "", filename = filename)
    return True
  except:
    return False

try:
  shutil.rmtree("files")
except:
  pass

os.mkdir("files")

bot = telebot.TeleBot(config.token)
@bot.message_handler(commands=['start'])
def start_handler(message):
  bot.send_message(
    message.chat.id,
    "Привет! Я бот, который может скачивать музыку с YouTube и YouTube Music.\n\nЧтоб скачивать музыку, тебе потребуется отправить ссылку на видео/трек с YouTube, а далее я отправлю аудио файл тебе. Всё просто! :)\n\nДоступные домены в ссылках:\n・ www.youtube.com\n・ youtube.com\n・ m.youtube.com\n・ music.youtube.com\n・ youtu.be"
  )

@bot.message_handler(commands=['debug'])
def start_handler(m):
  bot.send_message(m.chat.id, m)

@bot.message_handler(func=lambda message: True)
def message(m):
  if os.path.exists("files/" + str(m.chat.id)):
    return
  
  msg = bot.send_message(m.chat.id, "Скачиваю аудио...")
  if not is_user_subscribed(m.chat.id):
    bot.edit_message_text(
      chat_id = m.chat.id,
      message_id = msg.message_id,
      text = 
      "Чтоб пользоваться ботом, нужно присоединиться к каналу!\nt.me/DimLuxBlog"
    )
    return

  if not check_link(m.text):
    bot.edit_message_text(chat_id = m.chat.id,
                          message_id = msg.message_id,
                          text = "Это не ссылка на ютуб!")
    return

  yt = youtube(get_id(m.text))

  if yt == -1:
    bot.edit_message_text(
      chat_id = m.chat.id,
      message_id = msg.message_id,
      text = "Ошибка API: -1\nПричина: бот не получил доступа к YouTube."
    )
    return

  if yt == -2:
    bot.edit_message_text(
      chat_id = m.chat.id,
      message_id = msg.message_id,
      text = 
      "Ошибка API: -2\nПричина: бот не получил статус есть ли видео/трек на YouTube."
    )
    return

  if yt == -4:
    bot.edit_message_text(
      chat_id = m.chat.id,
      message_id = msg.message_id,
      text = "Ошибка API: -4\nПричина: бот получил другой ответ о статусе видео."
    )
    return

  if yt == -3:
    bot.edit_message_text(chat_id = m.chat.id,
                          message_id = msg.message_id,
                          text = "Этого видео/трека нет на YouTube!")
    return

  if yt["title"] == "ERROR" or yt["author"] == "ERROR" or yt[
      "length"] == "ERROR":
    bot.edit_message_text(
      chat_id = m.chat.id,
      message_id = msg.message_id,
      text = "Ошибка API: " + yt +
      "\nПричина: Ошибка получения информации о видео/треке.")
    return

  if int(yt["length"]) > 600:
    bot.edit_message_text(chat_id = m.chat.id,
                          message_id = msg.message_id,
                          text = "Это видео/трек длительности больше 10 минут")
    return

  os.mkdir("files/" + str(m.chat.id))

  if not get_thumb(get_id(m.text), "files/" + str(m.chat.id) + "/"):
    shutil.rmtree("files/" + str(m.chat.id))
    bot.edit_message_text(
      chat_id = m.chat.id,
      message_id = msg.message_id,
      text="Ошибка API: -6\nПричина: бот не получил доступ к обложке.")
    return

  if not get_audio_from_video(
      get_id(m.text), "files/" + str(m.chat.id) + "/" + yt["author"] + " - " +
      yt["title"] + ".m4a"):
    shutil.rmtree("files/" + str(m.chat.id))
    bot.edit_message_text(
      chat_id = m.chat.id,
      message_id = msg.message_id,
      text = 
      "Ошибка API: -5\nПричина: возможно YouTube блокирует доступ к получению аудио файлу."
    )
    return

  if not add_audiotag(
      "files/" + str(m.chat.id) + "/" + yt["author"] + " - " + yt["title"] +
      ".m4a", yt["title"], yt["author"],
      "files/" + str(m.chat.id) + "/thumb.jpg"):
    bot.edit_message_text(
      chat_id = m.chat.id,
      message_id = msg.message_id,
      text = "Ошибка: не получилось добавить аудиотеги и обложку к треку.")

  audio = open(
    "files/" + str(m.chat.id) + "/" + yt["author"] + " - " + yt["title"] +
    ".m4a", "rb")

  thumbnail = open("files/" + str(m.chat.id) + "/thumb.jpg", "rb")

  bot.edit_message_text(chat_id=m.chat.id,
                        message_id = msg.message_id,
                        text = "Отправляю аудио файл...")
  bot.send_audio(m.chat.id,
                 audio,
                 title = yt["title"],
                 performer = yt["author"],
                 thumb = thumbnail)
  bot.delete_message(m.chat.id, msg.message_id)
  
  shutil.rmtree("files/" + str(m.chat.id))

if config.isReplit:
  from flask import Flask
  from threading import Thread
  app = Flask('1')
  @app.route('/')
  def main():
    return ""
  def run():
    app.run(host="0.0.0.0", port=8080)
  def keep_alive():
    server = Thread(target=run)
    server.start()
  keep_alive()

os.system("clear")
try:
  bot.polling()
except:
  sys.exit(os.system("python3 main.py"))