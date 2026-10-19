package Agent

import (
	"Client/middle"
	"database/sql"
	"github.com/gin-gonic/gin"
)

func StartAgentHandle(r *gin.Engine, db *sql.DB) {
	agent := r.Group("/api/agent")
	answer := agent.Group("/answer")
	answer.POST("/text", middle.VerifyUuid(db), func(c *gin.Context) {
		Uuid := c.PostForm("uuid")
		Question := c.PostForm("question")
		c.JSON(200, gin.H{"message": "Agent started"})
	})
}
