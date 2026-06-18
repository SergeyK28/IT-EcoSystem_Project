# БЕЗОПАСНО (параметризованный запрос)
cursor.execute(
    "SELECT * FROM Client WHERE Login = %s AND PasswordHash = %s",
    (login, password_hash)
)
