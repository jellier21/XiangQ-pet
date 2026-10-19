package main

import (
	"Client/handle"
	"Client/sqldb"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"log"
	"os"
)

func main() {
	err := godotenv.Load(".env.net")
	if err != nil {
		log.Printf("加载env.net失败: %v", err)
		return
	}
	serve := gin.Default()
	db := sqldb.InitSql()

	handle.ClientHandleStart(serve, db)

	log.Printf("服务启动成功，服务启动在: http://%s%s", os.Getenv("HOST"), os.Getenv("NET_PORT"))
	err = serve.Run(os.Getenv("NET_PORT"))
	if err != nil {
		log.Printf("启动服务失败: %v", err)
		return
	}

}
