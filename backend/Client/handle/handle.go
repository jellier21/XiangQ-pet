package handle

import (
	"Client/handle/Agent"
	"Client/handle/User"
	"database/sql"
	"github.com/gin-gonic/gin"
)

func ClientHandleStart(r *gin.Engine, db *sql.DB) {
	r.GET("/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"message": "pong",
		})
	})
	User.StartUserHandle(r, db)
	Agent.StartAgentHandle(r, db)
}
