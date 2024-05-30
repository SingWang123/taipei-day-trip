from fastapi import *
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from typing import Optional
app=FastAPI()

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
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "12345678",
    database = "taipei_attractions"
)

mycursor = mydb.cursor(dictionary = True)

#/api/attractions 取得景點資料列表 (用query param方式帶參數)
@app.get("/api/attractions")
async def attractions(page : int = 0, keyword : Optional[str] = None):
	return "123"




#/api/attraction/{attractionID} 根據景點編號，取得景點資料
@app.get("/api/attraction/{attractionID}")
async def get_attraction(attractionID:int):
	sql = "select id, name, category, description, address, transport, mrt, lat, lng from data where id = %s "
	sql_img = "select img_url from images where data_id = %s" 
	val = (attractionID,)
	mycursor.execute(sql,val)
	attraction_result = mycursor.fetchall()

	images = []
	mycursor.execute(sql_img,val)
	img_result = mycursor.fetchall()
	for img in img_result:
		images.append(img["img_url"])
	
	# 將圖片合到結果的字典檔
	attraction_result[0]["images"] = images

	if len(attraction_result) == 0:
		return JSONResponse(
            status_code = 400,
            content = {
                "error": True,
                "message": "景點編號不正確",
            }
        )
	else:
		return JSONResponse(content = {	
			"data":attraction_result[0]
        })
        

#/api/mrts 取得捷運站名稱列表
@app.get("/api/mrts")
async def get_mrts():
	sql = "select mrt from data group by mrt order by count(*) desc"
	mycursor.execute(sql)
	mrt_result = mycursor.fetchall()

	mrt_list = []
	for mrt in mrt_result:
		if mrt["mrt"] == None:
			pass
		else:
			mrt_list.append(mrt["mrt"])
			
	return JSONResponse(content= {
        "data":{
			"id":mrt_list
			}
        })


	# try:
	# 	print(afdd)
	# except:
	# 	raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="Test exception")

keyword = ""
page = 0

sql = ""
if len(keyword) == 0:
	sql = "select id, name, category, description, address, transport, mrt, lat, lng from data"
	mycursor.execute(sql)
else:
	sql = "select id, name, category, description, address, transport, mrt, lat, lng from data where  name like %s or mrt = %s"
	val = (f'%{keyword}%',keyword)
	mycursor.execute(sql,val)

search_result = mycursor.fetchall()


max_page = divmod(len(search_result),12)[0]
if page < max_page :
	

print(max_page)

attractions_data = []
i = page * 12
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

print(divmod(len(search_result),12))
#print(len(attraction_result))

# val = (50,)
# mycursor.execute(sql,val)
# attraction_result = mycursor.fetchall()

# images = []
# mycursor.execute(sql_imag,val)
# img_result = mycursor.fetchall()
# for img in img_result:
# 	images.append(img["img_url"])

# attraction_result[0]["images"] = images
# newdata = {"data":attraction_result[0]}

# print (newdata)

