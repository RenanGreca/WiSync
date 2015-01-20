#import urllib2
#response = urllib2.urlopen('http://192.168.1.132:8080/b.m4a')
#data = response.read()
#f = open('b.m4a', 'w')
#f.write(data)
#f.close

import urllib2, sys

def chunk_report(bytes_so_far, chunk_size, total_size, filename):
   percent = float(bytes_so_far) / total_size
   percent = round(percent*100, 2)
   sys.stdout.write("Baixando arquivo %s (%0.2f%%)\r" % (filename, percent))

   if bytes_so_far >= total_size:
      sys.stdout.write('\n')

def chunk_read(response, filename, chunk_size=8192, report_hook=None):
   total_size = response.info().getheader('Content-Length').strip()
   total_size = int(total_size)
   bytes_so_far = 0

   while 1:
      chunk = response.read(chunk_size)
      bytes_so_far += len(chunk)

      if not chunk:
         break

      if report_hook:
         report_hook(bytes_so_far, chunk_size, total_size, filename)

   return bytes_so_far

if __name__ == '__main__':
   response = urllib2.urlopen('http://192.168.1.132:8080/b.m4a');
   chunk_read(response, 'b.m4a', report_hook=chunk_report)

