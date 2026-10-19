package User

import (
	"Client/sqldb"
	"database/sql"
	"github.com/gin-gonic/gin"
	"log"
)

func StartUserHandle(r *gin.Engine, db *sql.DB) {
	user := r.Group("/api/user")
	user.POST("/register", func(c *gin.Context) {
		name := c.PostForm("name")
		uuid, err := sqldb.InsertUserReturnUuid(name, db)
		if err != nil {
			log.Printf("注册用户 %s 失败: %v", name, err)
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}
		markList := []string{"xx"}
		mark := false
		for _, item := range markList {
			if item == name {
				mark = true
				break
			}
		}
		c.JSON(200, gin.H{
			"uuid": uuid,
			"mark": mark,
		})
	})
}
