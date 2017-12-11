import sqlite3

db = sqlite3.connect("./misc/entries.db")

cursor = db.cursor()

cursor.execute('''
SELECT name, id, COUNT(*) FROM entries GROUP BY name
''')

result = "NAME | DISCORD_ID | COUNT\n"
result += "-" * len(result) + "\n"
for i in cursor.fetchall():
    result += "{:<4} | {:<9} | {:<5}\n".format(i[0], i[1], i[2])

with open("entries_dump.txt", "w") as f:
    f.write(result)

db.close()
