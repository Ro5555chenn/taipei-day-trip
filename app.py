from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import FileResponse, JSONResponse
import mysql.connector
from mysql.connector import Error
from typing import List, Optional, Dict, Any

app = FastAPI()

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

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="54.206.86.195",
            user="root",
            password="root",
            database="official_website"
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise HTTPException(status_code=500, detail="資料庫連接失敗")


@app.get("/api/attractions")
def get_attractions(
    page: int = Query(0, ge=0), 
    keyword: Optional[str] = None,
    mrt: Optional[str] = None
) -> Dict[str, Any]:
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        offset = page * 12 
        query = "SELECT * FROM attractions WHERE 1=1"
        params = []

        if keyword:
            query += " AND name LIKE %s"
            params.append(f"%{keyword}%")
        
        if mrt:
            query += " AND mrt = %s"
            params.append(mrt)

        query += " LIMIT 12 OFFSET %s"
        params.append(offset)

        print(f"Executing query: {query}")
        print(f"With parameters: {params}")

        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        connection.close()

        print(f"Query results: {results}")

        if not results:
            results = []  
            next_page = None 
        else:
            next_page = page + 1 if len(results) == 12 else None

        response_data = {"data": results}  
        response_data["nextPage"] = next_page  

        return response_data

    except Error as e:
        print(f"Error fetching data from MySQL: {e}")
        return JSONResponse(status_code=500, content={"error": True, "message": "無法獲取資料"})

# 根據景點編號取得景點資料 API
@app.get("/api/attraction/{attractionId}")
def get_attraction_by_id(attractionId: int) -> Dict[str, Any]:
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM attractions WHERE id = %s"
        cursor.execute(query, (attractionId,))
        attraction = cursor.fetchone()
        cursor.close()
        connection.close()

        if not attraction:
            return JSONResponse(status_code=400, content={"error": True, "message": "景點不存在"})

      
        images = [f"https://{url}" for url in attraction["file"].split("https://") if url]

        
        response_data = {
            "data": {
                "id": attraction["id"],
                "name": attraction["name"],
                "category": attraction["CAT"],
                "description": attraction["description"],
                "address": attraction["address"],
                "transport": attraction["direction"],
                "mrt": attraction["MRT"],
                "lat": attraction["latitude"],
                "lng": attraction["longitude"],
                "images": images  
            }
        }

        return response_data

    except Error as e:
        print(f"Error fetching attraction data from MySQL: {e}")
        return JSONResponse(status_code=500, content={"error": True, "message": "無法獲取景點資料"})


@app.get("/api/mrts")
def get_mrts() -> Dict[str, Any]:
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT mrt, COUNT(*) AS attraction_count 
            FROM attractions 
            WHERE mrt IS NOT NULL 
            GROUP BY mrt 
            ORDER BY attraction_count DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()

        if not results:
            results = []  

        mrt_list = [result['mrt'] for result in results]  

        response_data = {"data": mrt_list}

        return response_data

    except Error as e:
        print(f"Error fetching MRT data from MySQL: {e}")
        return JSONResponse(status_code=500, content={"error": True, "message": "無法獲取捷運站資料"})
