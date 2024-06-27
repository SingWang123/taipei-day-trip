from fastapi import *
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from backend.model import signup_check,signin_check,token_check

app = FastAPI()

# 設定CORS
origins = [
	"http://localhost:8000",   # 本地前端網址
	"http://localhost:3000",
	"http://54.168.177.59:8000",
]

app.add_middleware(
	CORSMiddleware,
	allow_origins = ["*"],  #origins,目前設定本地端抓不到，先關掉方便開發測試
	allow_credentials = True,
	allow_methods = ["*"],
	allow_headers = ["*"], 	
)

# 設定靜態檔案目錄
app.mount("/static", StaticFiles(directory="static"), name="static")

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")


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



# # model_確認該email是否已經存在，不存在就寫入資料
# def signup_check(name,email,password):
# 	connection = pool2.get_connection()
# 	mycursor = connection.cursor(dictionary = True)

# 	sql = "SELECT email FROM member WHERE email = %s"
# 	val = (email,)
# 	mycursor.execute(sql,val)
# 	signup_result = mycursor.fetchall()
	
# 	if len(signup_result) != 0:
# 		# 關閉資料庫連線
# 		connection.close()
# 		return {"ok" : False}  # 資料庫已有資料，無法註冊
# 	else:
# 		sql_insert = "INSERT INTO member (name, email, password) VALUES (%s, %s, %s)"
# 		val_insert = (name,email,password)
# 		mycursor.execute(sql_insert,val_insert)
# 		connection.commit()

# 		# 關閉資料庫連線
# 		connection.close()
# 		return {"ok" : True}  # 新增資料成功


# # model_驗證使用者帳密是否正確
# def signin_check(email,password):
# 	connection = pool2.get_connection()
# 	mycursor = connection.cursor(dictionary = True)

# 	sql = "SELECT email, password, name FROM member WHERE email = %s"
# 	val = (email,)
# 	mycursor.execute(sql,val)
# 	signin_result = mycursor.fetchall()

# 	if len(signin_result) == 0 :
# 		connection.close() # 關閉資料庫連線
# 		return {"ok" : False, "masseage" : "帳號不存在"}

# 	#pwd_context.verify 是 passlib 提供的方法，用來檢查純文本密碼是否與哈希密碼匹配。
# 	elif not pwd_context.verify(password,signin_result[0]["password"]):
# 		connection.close() # 關閉資料庫連線
# 		return {"ok" : False, "masseage" : "密碼不正確"}

# 	connection.close() # 關閉資料庫連線
# 	return {
# 		"ok" : True,
# 		"name" : signin_result[0]["name"]
# 	}
	

# # model_檢查使用者信箱是否存在
# def token_check(email):
# 	connection = pool2.get_connection()
# 	mycursor = connection.cursor(dictionary = True)

# 	sql = "SELECT id, name, email FROM member WHERE email = %s"
# 	val = (email,)
# 	mycursor.execute(sql,val)
# 	token_result = mycursor.fetchall()

# 	connection.close() # 關閉資料庫連線
# 	if len(token_result) == 0 :
# 		return {"ok" : False, "masseage" : "帳號不存在"}
# 	else:
# 		return {
# 			"ok" : True,
# 			"data" : {
# 				"id" : token_result[0]["id"],
# 				"email" : token_result[0]["email"],
# 				"name" : token_result[0]["name"]
# 			}
# 		}

# jwt_產出jwt token
def generate_token(name,email):	
	expire = datetime.now(timezone.utc) + timedelta(minutes = 1)  #timedelta(days = 7)
	data = {
		"name" : name ,
		"email" : email,
		"exp" : expire
	}
	
	encoded_jwt = jwt.encode(data,"CzpcHvTvrKZx",algorithm = "HS256")
	return(encoded_jwt)

# 驗證前端傳回來的token是否正確
def verify_token(token):
	try:
		#解碼token (jwt.decode 可能會有異常，需要捕獲異常)
		decode = jwt.decode(token , "CzpcHvTvrKZx" , algorithms= ["HS256"])

		#檢查token有沒有過期
		exp = decode.get("exp")
		if exp and datetime.fromtimestamp(exp,tz = timezone.utc) < datetime.now(timezone.utc):						
			return	{"ok" : False, "masseage" : "token已失效"}

		#檢查訊息和資料庫是否一致
		token_check_result = token_check(decode["email"]) 
		if token_check_result["ok"] == False:
			return	{"ok" : False, "masseage" : "帳號不存在"}
		
		return token_check_result #一切正確，回傳id name email
	
	except jwt.ExpiredSignatureError:
		return	{"ok" : False, "masseage" : "token已失效"}
	except jwt.JWTError:
		return	{"ok" : False, "masseage" : "token無效"}
		

#/api/user 註冊一個會員
@app.post("/api/user")
async def sign_up(request:Request):
	# 檢查使用者是否有登入
	# 用request.json() 來解析request傳來的json資料
	# data = await request.json()
	# name = data.get("name")
	# email = data.get("email")
	# hashed_password = pwd_context.hash(data.get("password") ) #將密碼用hash加密
	return (data)

	# 檢查使用者是否有註冊過，沒有的話就幫使用者註冊資料
	# signUpCheck = signup_check(name,email,hashed_password)
	
	# if signUpCheck ["ok"] == True:
	# 	return JSONResponse(
	# 		status_code = 200,
	# 		content = {
	# 			"ok": True
	# 		}
	# 	)
	# else:
	# 	return JSONResponse(
	#         status_code = 400,
	#         content = {
	#             "error": True,
	#             "message": "帳號已存在",
	#         }
	# 	)

#/api/auth 登入會員帳戶，成功的話取得token
@app.put("/api/auth")
async def sign_in(request:Request):
	# 檢查使用者是否有登入
	# 用request.json() 來解析request傳來的json資料
	data = await request.json()
	email = data.get("email")
	password = data.get("password")

	#檢查帳密是否正確
	signin_result = signin_check(email,password)
	
	if signin_result["ok"] == False:
		return JSONResponse(
	        status_code = 400,
	        content = {
	            "error": True,
	            "message": "帳號或密碼錯誤",
	        }
		)
	
	elif signin_result["ok"] == True: #正確的話就給予一個token
		jwt_token = generate_token(signin_result["name"],email)
		return JSONResponse(
			status_code = 200,
			content = {
				"token":  jwt_token
			}
		)

# 用於從請求的 Authorization header 中提取 Bearer Token。	
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

#/api/user/auth 確認會員登入狀態，取得當前登入會員的資料
@app.get("/api/user/auth")
async def check_signin(token: str = Depends(oauth2_scheme)): #astAPI 會自動調用 oauth2_scheme，這個依賴項會從請求的 Authorization header 中提取 Bearer Token。

	if token == "null":  # 目前沒有token的狀況
		return JSONResponse(
			status_code = 200,
			content = {"data" : None}
		)	
		
	verify_result = verify_token(token)
		
	if verify_result["ok"] == False:
		return JSONResponse(
			status_code = 200,
			content = {"data" : None}
		)
	return JSONResponse(
		status_code = 200,
		content = {"data" : verify_result["data"]}
	)


#/api/attractions 取得景點資料列表 (用query param方式帶參數)
@app.get("/api/attractions")
async def attractions(page : int = 0, keyword : Optional[str] = None):
	
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
		
		return JSONResponse(
	        status_code = 400,
	        content = {
	            "error": True,
	            "message": "查無資料",
	        }
		)
	
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

	# 依據搜尋結果總數，計算分頁的資料
	max_page = divmod(max_result[0]['count(*)'],12)[0]

	if page == max_page:
		# 搜尋結果 =<12筆，一頁就能滿足的情況，或是最後一頁
		next_page = None
	elif page < max_page:
		next_page = page + 1
	elif page > max_page:
		return JSONResponse(
	        status_code = 400,
	        content = {
	            "error": True,
	            "message": "此分頁無資料",
	        }
		)

	return JSONResponse(content = {	
		"nextPage" : next_page,
		"data" : attractions_data
    })


#/api/attraction/{attractionID} 根據景點編號，取得景點資料
@app.get("/api/attraction/{attractionID}")
async def get_attraction(attractionID : int):
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
		return JSONResponse(
            status_code = 400,
            content = {
                "error": True,
                "message": "景點編號不正確",
            }
        )

	images = []
	for img in img_result:
		images.append(img["img_url"])
	
	# 將圖片合到結果的字典檔
	attraction_result[0]["images"] = images

	return JSONResponse(content = {	
		"data":attraction_result[0]
    })
        

#/api/mrts 取得捷運站名稱列表
@app.get("/api/mrts")
async def get_mrts():
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
			
	return JSONResponse(content= {
        "data":
			mrt_list
        })
