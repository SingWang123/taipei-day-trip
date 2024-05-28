# 導入json資料，處理資料
import json

jsonFile = open('data/taipei-attractions.json','r', encoding = 'utf-8')
a = json.load(jsonFile)

result = a['result']['results'][0]

data = []
i = 0
while i < 58:
    data.append(a['result']['results'][i])
    i += 1

# 整理圖片資料
imagex = []
image = data[0]['file'].split('https')
for i in image:
    if i == "":
        print("空的")
    else:
        imagex.append("https"+i)
        print("https"+i)
        print(i[-1:-4])





# print(data[0]['name'], data[0]['CAT'], data[0]['MRT'], data[0]['description'], data[0]['address'], data[0]['direction'], data[0]['latitude'], data[0]['longitude'])



# for i in data[0]:
#     print(data[0][i])


# 連接上資料庫
import mysql.connector
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "12345678",
    database = "taipei_attractions"
)

mycursor = mydb.cursor()


# 塞資料進去 data表,

# i = 0
# while i < 58:
#     sql = "insert into data (name, category, mrt, description, address, transport, lat, lng) values (%s, %s, %s, %s, %s, %s, %s, %s)"
#     val = ((data[i]['name'], data[i]['CAT'], data[i]['MRT'], data[i]['description'], data[i]['address'], data[i]['direction'], data[i]['latitude'], data[i]['longitude']))
#     mycursor.execute(sql,val)
#     mydb.commit()
#     i += 1


# sql = "describe data"
# mycursor.execute(sql)
# test = mycursor.fetchall()



# sql = "describe data"
# mycursor.execute(sql)
# test = mycursor.fetchall()

# print(test)




# i = 0
# while i < 58:
#     print (a['result']['results'][i]['latitude'])
#     i += 1


# for i in result:
#     print(i)

# split = result.split(',')
# print(split)

# for i in a['re]
#      print(i,a[i])

#需求資料：景點名稱('name')、景點分類('cat')、捷運站位置('MRT')、描述('description')、地址('address')、交通方式('direction')、經度('longitude')、緯度('latitude')、圖片('file')