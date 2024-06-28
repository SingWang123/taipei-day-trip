from fastapi import *
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 連接上資料庫
import mysql.connector
from mysql.connector import pooling
import mysql.connector.pooling

# 設定連接參數
dbconfig = {
    "host" : "localhost",
    "user" : "root",
    "password" : "12345678",
    "database" : "taipei_attractions"
}

# 創建Connection pool
pool2 = pooling.MySQLConnectionPool(
	pool_name = "mypool",
	pool_size = 5,
	pool_reset_session = True,
	**dbconfig 
)

#初始化 CryptContext
import jwt
from passlib.context import CryptContext
pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")


# model_確認該email是否已經存在，不存在就寫入資料
def signup_check(name,email,password):
	connection = pool2.get_connection()
	mycursor = connection.cursor(dictionary = True)

	sql = "SELECT email FROM member WHERE email = %s"
	val = (email,)
	mycursor.execute(sql,val)
	signup_result = mycursor.fetchall()
	
	if len(signup_result) != 0:
		# 關閉資料庫連線
		connection.close()
		return {"ok" : False}  # 資料庫已有資料，無法註冊
	else:
		sql_insert = "INSERT INTO member (name, email, password) VALUES (%s, %s, %s)"
		val_insert = (name,email,password)
		mycursor.execute(sql_insert,val_insert)
		connection.commit()

		# 關閉資料庫連線
		connection.close()
		return {"ok" : True}  # 新增資料成功


# model_驗證使用者帳密是否正確
def signin_check(email,password):
	connection = pool2.get_connection()
	mycursor = connection.cursor(dictionary = True)

	sql = "SELECT email, password, name FROM member WHERE email = %s"
	val = (email,)
	mycursor.execute(sql,val)
	signin_result = mycursor.fetchall()

	if len(signin_result) == 0 :
		connection.close() # 關閉資料庫連線
		return {"ok" : False, "masseage" : "帳號不存在"}

	#pwd_context.verify 是 passlib 提供的方法，用來檢查純文本密碼是否與哈希密碼匹配。
	elif not pwd_context.verify(password,signin_result[0]["password"]):
		connection.close() # 關閉資料庫連線
		return {"ok" : False, "masseage" : "密碼不正確"}

	connection.close() # 關閉資料庫連線
	return {
		"ok" : True,
		"name" : signin_result[0]["name"]
	}
	

# model_檢查使用者信箱是否存在
def token_check(email):
	connection = pool2.get_connection()
	mycursor = connection.cursor(dictionary = True)

	sql = "SELECT id, name, email FROM member WHERE email = %s"
	val = (email,)
	mycursor.execute(sql,val)
	token_result = mycursor.fetchall()

	connection.close() # 關閉資料庫連線
	if len(token_result) == 0 :
		return {"ok" : False, "masseage" : "帳號不存在"}
	else:
		return {
			"ok" : True,
			"data" : {
				"id" : token_result[0]["id"],
				"email" : token_result[0]["email"],
				"name" : token_result[0]["name"]
			}
		}
	

# model_取得index頁資料
def get_index(page,keyword):
	# 連線到資料庫
	connection = pool2.get_connection()
	mycursor = connection.cursor(dictionary = True)
	
	# 依據有沒有keyword值，使用不同的搜尋語法
	if keyword == None:
		sql = "select id, name, category, description, address, transport, mrt, lat, lng from data limit %s, 12"
		val = (page * 12,)
		mycursor.execute(sql,val)
		search_result = mycursor.fetchall()

		#取得搜尋結果總數
		sql = "select count(*) from data"
		mycursor.execute(sql)
		max_result = mycursor.fetchall()
	else:
		sql = "select id, name, category, description, address, transport, mrt, lat, lng from data where name like %s or mrt = %s limit %s, 12"
		val = (f'%{keyword}%',keyword, page * 12)
		mycursor.execute(sql,val)
		search_result = mycursor.fetchall()

		#取得搜尋結果總數
		sql = "select count(*) from data where name like %s or mrt = %s"
		val = (f'%{keyword}%',keyword)
		mycursor.execute(sql,val)
		max_result = mycursor.fetchall()

	# 若搜尋結果無資料，直接回傳查無資料
	if max_result[0]['count(*)'] == 0:
		# 關閉資料庫連線
		connection.close()
		
		return {"ok" : False, "masseage" : "查無資料"}
	
	# 整理搜尋結果的景點資料，並加上對應的景點圖片	
	attractions_data = []
	i = 0
	while i < len(search_result) :
		# 依序抓取搜尋結果的對應圖片資料
		sql_img = "select img_url from images where data_id = %s" 
		val = (search_result[i]['id'],)
		mycursor.execute(sql_img,val)
		img_result = mycursor.fetchall()
		
		images = []
		for img in img_result:
			images.append(img["img_url"])

		search_result[i]["images"] = images
		attractions_data.append(search_result[i])
		
		i += 1

	# 關閉資料庫連線
	connection.close()
	
	return {
		"ok" : True,
		"max_result" : max_result[0]['count(*)'],
		"attractions_data" : attractions_data
	}


# model_取得景點資料
def get_attractiondata(attractionID):
	# 連線到資料庫
	connection = pool2.get_connection()
	mycursor = connection.cursor(dictionary = True)
	
	# 搜尋景點資料
	sql = "select id, name, category, description, address, transport, mrt, lat, lng from data where id = %s "
	val = (attractionID,)
	mycursor.execute(sql,val)
	attraction_result = mycursor.fetchall()
	# 搜尋景點圖片
	sql_img = "select img_url from images where data_id = %s" 
	mycursor.execute(sql_img,val)
	img_result = mycursor.fetchall()

	# 關閉資料庫連線
	connection.close()

	# 搜尋沒有找到資料時，回傳景點編號不正確
	if len(attraction_result) == 0:
		return {
                "ok": False,
                "message": "景點編號不正確",
            }
    
	images = []
	for img in img_result:
		images.append(img["img_url"])
	
	# 將圖片合到結果的字典檔
	attraction_result[0]["images"] = images

	return {
		"ok" : True,
		"data" : attraction_result[0]
	}

# model_取得捷運站排序
def get_mrtdata():
	# 連線到資料庫
	connection = pool2.get_connection()
	mycursor = connection.cursor(dictionary = True)
	
	sql = "select mrt from data group by mrt order by count(*) desc"
	mycursor.execute(sql)
	mrt_result = mycursor.fetchall()

	# 關閉資料庫連線
	connection.close()

	mrt_list = []
	for mrt in mrt_result:
		if mrt["mrt"] == None:
			pass
		else:
			mrt_list.append(mrt["mrt"])
	
	return {
		"ok" : True,
		"data" : mrt_list
	}

# model_建立旅遊行程，在member中寫入旅遊行程
def booking_data(id,attractionID,date,time,price):
	try:
		# 連線到資料庫
		connection = pool2.get_connection()
		mycursor = connection.cursor(dictionary = True)
		
		sql = "update member set last_signin_time = CURRENT_TIMESTAMP, data_id = %s, date = %s, time = %s, price = %s where id = %s "
		val = (attractionID,date,time,price,id)
		mycursor.execute(sql,val)
		
		connection.commit()

		return {"ok" : True}
	
	except mysql.connector.Error as err:
		return {"ok" : False, "message" : f"資料庫寫入錯誤:{err}"}
	
	except Exception as e:
		return {"ok" : False, "message" : f"未知錯誤:{e}"}
	
	finally:
		if mycursor:
			mycursor.close()
		if connection:
			connection.close()

# model_檢查使用者有沒有旅遊行程，有的話撈出資料
def check_booking(id):
	try:
		# 連線到資料庫
		connection = pool2.get_connection()
		mycursor = connection.cursor(dictionary = True)
		
		# 先確認該ID有沒有booking資料
		sql = "select data_id, date, time, price from member where id = %s "
		val = (id,)
		mycursor.execute(sql,val)
		result = mycursor.fetchall()
		
		if result[0]["data_id"] == None:
			return {"ok" : False, "message" : "沒有預約行程"}
	
		# 用預約的地點ID撈取旅遊行程資料
		sql = "select id, name, address from data where id = %s "
		val = (result[0]["data_id"],)
		mycursor.execute(sql,val)
		result_attraction = mycursor.fetchall()

		# 用預約的地點ID撈取旅遊地點的圖片
		sql = "select img_url from images where data_id = %s "
		val = (result[0]["data_id"],)
		mycursor.execute(sql,val)
		result_images = mycursor.fetchall()

		result_attraction[0]["image"] = result_images[0]["img_url"]

		return {
			"ok" : True,
			"data": {
				"attraction":result_attraction[0],
				"date" : result[0]["date"],
				"time" : result[0]["time"],
				"price" : result[0]["price"]		
			}
		}

	except mysql.connector.Error as err:
		return {"ok" : False, "message" : f"資料庫寫入錯誤:{err}"}
	
	except Exception as e:
		return {"ok" : False, "message" : f"未知錯誤:{e}"}
	
	finally:
		if mycursor:
			mycursor.close()
		if connection:
			connection.close()

# model_刪除旅遊行程，在member將旅遊行程的欄位清空
def delete_bookingdata(id):
	try:
		# 連線到資料庫
		connection = pool2.get_connection()
		mycursor = connection.cursor(dictionary = True)
		
		sql = "update member set last_signin_time = CURRENT_TIMESTAMP, data_id = null, date = null, time = null, price = null where id = %s "
		val = (id,)
		mycursor.execute(sql,val)
		
		connection.commit()

		return {"ok" : True}
	
	except mysql.connector.Error as err:
		return {"ok" : False, "message" : f"資料庫寫入錯誤:{err}"}
	
	except Exception as e:
		return {"ok" : False, "message" : f"未知錯誤:{e}"}
	
	finally:
		if mycursor:
			mycursor.close()
		if connection:
			connection.close()

