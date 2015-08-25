import ftplib

ftp = ftplib.FTP("192.168.1.132")
ftp.login("user", "12345")

data = []

ftp.dir(data.append)

ftp.quit()

for line in data:
    print "-", line
