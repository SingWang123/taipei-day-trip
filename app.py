from fastapi import *
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from backend.model import *

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



#初始化 CryptContext
import jwt
from passlib.context import CryptContext
pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")


# jwt_產出jwt token
def generate_token(name,email):	
	expire = datetime.now(timezone.utc) + timedelta(days = 7)  #timedelta(days = 7)
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
	# 用request.json() 來解析request傳來的json資料
	data = await request.json()
	name = data.get("name")
	email = data.get("email")
	hashed_password = pwd_context.hash(data.get("password") ) #將密碼用hash加密

	# 檢查使用者是否有註冊過，沒有的話就幫使用者註冊資料
	signUpCheck = signup_check(name,email,hashed_password)
	
	if signUpCheck ["ok"] == True:
		return JSONResponse(
			status_code = 200,
			content = {
				"ok": True
			}
		)
	else:
		return JSONResponse(
	        status_code = 400,
	        content = {
	            "error": True,
	            "message": "帳號已存在",
	        }
		)

#/api/auth 登入會員帳戶，成功的話取得token
@app.put("/api/auth")
async def sign_in(request:Request):
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
	result = get_index(page,keyword)

	# 若搜尋結果無資料，直接回傳查無資料
	if result["ok"] == False:
		return JSONResponse(
	        status_code = 400,
	        content = {
	            "error": True,
	            "message": "查無資料",
	        }
		)

	max_result = result["max_result"]

	# 依據搜尋結果總數，計算分頁的資料
	max_page = divmod(max_result,12)[0]

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
		"data" : result["attractions_data"]
    })


#/api/attraction/{attractionID} 根據景點編號，取得景點資料
@app.get("/api/attraction/{attractionID}")
async def get_attraction(attractionID : int):

	result = get_attractiondata(attractionID)

	# 搜尋沒有找到資料時，回傳景點編號不正確
	if result["ok"] == False:
		return JSONResponse(
            status_code = 400,
            content = {
                "error": True,
                "message": "景點編號不正確",
            }
        )

	return JSONResponse(content = {	
		"data" : result["data"]
    })
        

#/api/mrts 取得捷運站名稱列表
@app.get("/api/mrts")
async def get_mrts():

	result = get_mrtdata()
			
	if result["ok"] == True:
		return JSONResponse(content= {
			"data":
				result["data"]
			})


#/api/booking get booking頁的資料
@app.get("/api/booking")
async def get_booking(request:Request, token: str = Depends(oauth2_scheme)):
	# 檢查使用者是否有登入
	if token == "null":  # 目前沒有token的狀況
		return JSONResponse(
			status_code = 403,
			content = {
				"error" : True,
				"message" : "未登入系統，拒絕存取"
			}
		)	

	verify_result = verify_token(token)
	
	if verify_result["ok"] == False:  # 驗證token錯誤的狀況
		return JSONResponse(
			status_code = 403,
			content = {
				"error" : True,
				"message" : verify_result["message"]
			}
		)

	# 檢查使用者是否有預定行程
	id = verify_result["data"]["id"]
	check_booking_result = check_booking(id)

	if check_booking_result["ok"] == False:
		return JSONResponse(
			status_code = 200,
			content = {"data" : None}
		)
	return JSONResponse(
		status_code = 200,
		content = {"data" : check_booking_result["data"]}
	)



#/api/booking 建立新的預定行程
@app.post("/api/booking")
async def post_booking(request:Request, token: str = Depends(oauth2_scheme)):
	# 檢查使用者是否有登入
	if token == "null":  # 目前沒有token的狀況
		return JSONResponse(
			status_code = 403,
			content = {
				"error" : True,
				"message" : "未登入系統，請先登入"
			}
		)	

	verify_result = verify_token(token)
	
	if verify_result["ok"] == False:  # 驗證token錯誤的狀況
		return JSONResponse(
			status_code = 403,
			content = {
				"error" : True,
				"message" : verify_result["message"]
			}
		)
	
	id = verify_result["data"]["id"]
	# 用request.json() 來解析request傳來的json資料
	data = await request.json()
	attractionID = data.get("attractionID")
	date = data.get("date")
	time = data.get("time")
	price = data.get("price")

	# 預定行程，寫入資料庫
	result = booking_data(id,attractionID,date,time,price)

	if result["ok"] == False:
		return JSONResponse(
			status_code = 400,
			content = {
				"error" : True,
				"message" : result["message"]
			}
		)
	return JSONResponse(
		status_code = 200,
		content = {
			"ok" : True
		}
	)

#/api/booking 刪除預定行程
@app.delete("/api/booking")
async def delete_booking(token: str = Depends(oauth2_scheme)):
	# 檢查使用者是否有登入
	if token == "null":  # 目前沒有token的狀況
		return JSONResponse(
			status_code = 403,
			content = {
				"error" : True,
				"message" : "未登入系統，請先登入"
			}
		)	

	verify_result = verify_token(token)
	
	if verify_result["ok"] == False:  # 驗證token錯誤的狀況
		return JSONResponse(
			status_code = 403,
			content = {
				"error" : True,
				"message" : verify_result["message"]
			}
		)
	
	id = verify_result["data"]["id"]
	name = verify_result["data"]["name"]  # 有評估是否要存信用卡資料上的會員名稱，但似乎沒必要，應以產品上的會員名稱為主


	# 刪除行程
	result = delete_bookingdata(id,)

	if result["ok"] == False:
		return JSONResponse(
			status_code = 400,
			content = {
				"error" : True,
				"message" : result["message"]
			}
		)
	return JSONResponse(
		status_code = 200,
		content = {
			"ok" : True
		}
	)


import httpx

#/api/orders 支付訂單
@app.post("/api/orders")
async def post_order(request:Request, token: str = Depends(oauth2_scheme)):
	# 檢查使用者是否有登入
	if token == "null":  # 目前沒有token的狀況
		return JSONResponse(
			status_code = 403,
			content = {
				"error" : True,
				"message" : "未登入系統，請先登入"
			}
		)	

	verify_result = verify_token(token)
	
	if verify_result["ok"] == False:  # 驗證token錯誤的狀況
		return JSONResponse(
			status_code = 403,
			content = {
				"error" : True,
				"message" : verify_result["message"]
			}
		)
	
	data = await request.json()
	contact = data.get("order").get("contact")

	# 確定有收到資料，先將訂單寫入資料庫，設定成UNPAID
	# 建立寫入資料庫要的資料
	id = verify_result["data"]["id"]
	name = verify_result["data"]["name"]
	
	data_id = data.get("order").get("trip").get("attraction").get("id")
	date = data.get("order").get("trip").get("date")
	time = data.get("order").get("trip").get("time")
	price = data.get("order").get("price")

	create_result = create_orderhistory(name, id, data_id, date, time, price)
	if create_result["ok"] == False:   # 寫入資料庫失敗
		return JSONResponse(
				status_code = 400,
				content = {
					"error" : True,
					"message" : result["message"]
				}
		)
	
	else:
		# 設定要傳到Tappay驗證的資料
		url = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
		headers = {
			'Content-Type': 'application/json',
			'x-api-key': 'partner_dzYGwE0yZTNnnGgCAWI7WS0sh3Iu4z79ozHB2TulbngO4tONWJXqIx9G'
		}
		post_data = {
			"prime": data.get("prime"),
			"partner_key": 'partner_dzYGwE0yZTNnnGgCAWI7WS0sh3Iu4z79ozHB2TulbngO4tONWJXqIx9G',
			"merchant_id": "gnissing_CTBC",
			"details": "TapPay Test",
			"amount": data.get("order").get("price"),
			"cardholder": {
				"phone_number" : contact["phone"],
				"name" : contact["name"],
				"email" : contact["email"]
			},
			"remember": True
		}
		
		# 傳送資料去tappay驗證
		async with httpx.AsyncClient() as client:
			response = await client.post(url, json=post_data, headers=headers)
			response_data = response.json()
		
		# 將驗證結果和付款資料寫入資料庫，取得交易代號

		if response_data["status"] == 0:  # status = 0 表示交易成功
			result = updata_order_result("success", create_result["order_id"])       # 資料庫更新資料
			delete_result = delete_bookingdata(id,)                                  # 刪除購物車資料
			
			if result["ok"] == True and delete_result["ok"] == True:   # 寫入資料庫成功
				return JSONResponse(
					status_code = 200,
					content = {
						"data": {
							"number": result["number"],
							"payment": {
								"status": 0,
								"message": "付款成功"
							}
						}
					}
				)
			else: # 寫入資料庫失敗
				return JSONResponse(
					status_code = 400,
					content = {
						"error" : True,
						"message" : result["message"]
					}
				)
		else:   # status 不是0 表示交易失敗，但建立訂單編號成功
			result_error = updata_order_result("failed", create_result["order_id"]) # 寫入支付失敗資料
			if result_error["ok"] :		
				return JSONResponse(
					status_code = 200,
					content = {
						"data": {
							"number": result_error["number"],
							"payment": {
								"status": 1,
								"message": response_data["msg"]
							}
						}
					}
				)	
			else:# 寫入資料庫失敗
				return JSONResponse(
					status_code = 400,
					content = {
						"error" : True,
						"message" : result["message"]
					}
				)

		

