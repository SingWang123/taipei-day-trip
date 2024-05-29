from fastapi import *
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
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

# /api/attractions 取得景點資料列表 (用query param方式帶參數)
# @app.get("/api/attractions")
# async def attractions(request:Request, page = int, keyword = str):
#     sql = "SELECT id, name, username From member WHERE username = %s"
#     val = (query_username,)
#     mycursor.execute(sql,val)
#     memberdata = mycursor.fetchall()
#     # 如果找不到用戶帳號，回傳"data":null
#     if request.session["SIGNED-IN"] == False or len(memberdata) == 0:
#         return JSONResponse(content = {"data":None})
#     else:
#         return JSONResponse(content= {
#             "data":{
#                 "id" : memberdata[0][0],
#                 "name" : memberdata[0][1],
#                 "username" : memberdata[0][2]
#             }
#         })


#/api/attraction/{attractionID} 根據景點編號，取得景點資料
@app.get("/api/attraction/{attractionID}")
async def get_attraction(request:Request, attractionID:int):
	sql = "select id, name, category, description, address, transport, mrt, lat, lng from data where id = %s "
	sql_imag = "select img_url from images where data_id = %s" 
	val = (attractionID,)
	mycursor.execute(sql,val)
	attraction_result = mycursor.fetchall()
	#print(mrt_result[0]['name'])

	images = []
	mycursor.execute(sql_imag,val)
	img_result = mycursor.fetchall()
	for img in img_result:
		images.append(img["img_url"])
	
	if len(attraction_result) == 0:
		return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "message": "景點編號不正確",
            }
        )
	else:
		return JSONResponse(content = {
			"data":{
				"id" : attraction_result[0]["id"],
				"name" : attraction_result[0]["name"],
				"category" : attraction_result[0]["category"],
				"description" : attraction_result[0]["description"],
				"address" : attraction_result[0]["address"],
				"transport" : attraction_result[0]["transport"],
				"mrt" : attraction_result[0]["mrt"],
				"lat" : attraction_result[0]["lat"],
				"lng" : attraction_result[0]["lng"],
				"images" : images
			}
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


sql = "select id, name, category, description, address, transport, mrt, lat, lng from data where id = %s "
sql_imag = "select img_url from images where data_id = %s" 
val = (88,)
mycursor.execute(sql,val)
attraction_result = mycursor.fetchall()
print(len(attraction_result))

images = []
mycursor.execute(sql_imag,val)
img_result = mycursor.fetchall()
for img in img_result:
	images.append(img["img_url"])
