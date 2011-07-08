import urllib

# get the Recaptcha state.
url = "https://www.google.com/recaptcha/api/challenge?k=6Lf8usUSAAAAADQcD-_h15PNkbrumALSPAZet8Hh"
resock = urllib.urlopen(url)
data = resock.read()
resock.close()

# extract the recaptcha state part of the string
print data
docloc = data.find("document.write")
print docloc

recaptchaState = data[:docloc]
print recaptchaState

f = open('tmp123.py', 'r+')
f.write(recaptchaState)
f.close()

f = open('../../media/js/google/recState.js', 'r+')
f.write(recaptchaState)
f.close()
