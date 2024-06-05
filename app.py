from fastapi import *
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI()

# 設定CORS
origins = [
	"http://localhost:8000",   # 本地前端網址
	"http://54.168.177.59:8000/",
]

app.add_middleware(
	CORSMiddleware,
	allow_origins = origins,
	allow_credentials = True,
	allow_methods = ["*"],
	allow_headers = ["*"],
)

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
		# 依序抓去搜尋結果的對應圖片資料
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
