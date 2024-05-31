# 導入json資料，處理資料
import json

jsonFile = open('data/taipei-attractions.json','r', encoding = 'utf-8')
a = json.load(jsonFile)

data = []
i = 0
while i < 58:
    data.append(a['result']['results'][i])
    i += 1


# 連接上資料庫
import mysql.connector
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "12345678",
    database = "taipei_attractions"
)

mycursor = mydb.cursor()

# 需求資料：景點名稱('name')、景點分類('CAT')、捷運站位置('MRT')、描述('description')、地址('address')、交通方式('direction')、經度('longitude')、緯度('latitude')、圖片('file')
# 塞資料進去 data表
def add_data():
    i = 0
    while i < 58:
        sql = "insert into data (name, category, mrt, description, address, transport, lat, lng) values (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = ((data[i]['name'], data[i]['CAT'], data[i]['MRT'], data[i]['description'], data[i]['address'], data[i]['direction'], data[i]['latitude'], data[i]['longitude']))
        mycursor.execute(sql,val)
        mydb.commit()
        i += 1

add_data()

# 塞資料進去image表
def add_image():
    i = 0
    while i < 58:
        # 撈出景點對應的ID
        sql = "select id from data where name = %s"
        val = (data[i]['name'],)
        mycursor.execute(sql,val)
        data_id = mycursor.fetchall()
        
        # 處理圖片網址
        images = data[i]['file'].split('https')
        for image in images:
            if image == "":
                pass
            elif image[-4:].lower() != ".jpg" and image[-4:].lower() != ".png" :
                pass
            else:
                # 塞入資料
                sql = "insert into images (data_id, img_url) values (%s, %s)"
                val = (data_id[0][0],"https" + image)
                mycursor.execute(sql,val)
                mydb.commit()
        i += 1

add_image()

