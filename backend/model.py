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