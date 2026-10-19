package sqldb

import (
	"database/sql"
	uuid2 "github.com/google/uuid"
)

func InsertUserReturnUuid(name string, db *sql.DB) (string, error) {
	sqlStr := "INSERT INTO user (uuid, name) VALUES (?, ?)"
	uuid := uuid2.NewString()
	_, err := db.Exec(sqlStr, uuid, name)
	if err != nil {
		return "", err
	}
	return uuid, nil
}

func VerifyUuidSql(uuid string, db *sql.DB) error {
	sqlStr := "SELECT * FROM user WHERE uuid = ?"
	_, err := db.Exec(sqlStr, uuid)
	if err != nil {
		return err
	}
	return nil
}
