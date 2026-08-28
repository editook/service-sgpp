import sqlite3

conn = sqlite3.connect('sgpp_test.db')
c = conn.cursor()

try:
    c.execute("DROP INDEX ix_casos_codigo_unico")
    c.execute("CREATE INDEX ix_casos_codigo_unico ON casos (codigo_unico)")
    conn.commit()
    print("Successfully changed ix_casos_codigo_unico from UNIQUE to non-unique.")
except Exception as e:
    print("Error:", e)

conn.close()
