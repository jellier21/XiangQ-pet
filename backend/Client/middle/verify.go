package middle

import (
	"Client/sqldb"
	"database/sql"
	"github.com/gin-gonic/gin"
)

func VerifyUuid(db *sql.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		Uuid := c.PostForm("uuid")
		err := sqldb.VerifyUuidSql(Uuid, db)
		if err != nil {
			c.JSON(401, gin.H{"error": "Invalid UUID"})
			c.Abort()
			return
		}
		c.Next()
	}
}
