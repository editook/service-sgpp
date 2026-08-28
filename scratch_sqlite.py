import sqlite3

conn = sqlite3.connect('sgpp_test.db')
c = conn.cursor()

c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='casos'")
res = c.fetchone()
if res:
    print(res[0])
print('---')
c.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='casos'")
for row in c.fetchall():
    print(row)
conn.close()
