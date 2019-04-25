import re,os
data = ""
pyFiles = ["main.py"]
numFile = 0

for path, subdirs, files in os.walk("./"):
    for name in files:
        if(re.match(r'.*\.py', name, re.I) and name != 'python2C.py' and path is "./" and name != 'boot.py' and name != "main.py"):
            pyFiles.append(os.path.join(path, name))

print(pyFiles)
numFile = len(pyFiles)
for pyFile in pyFiles:
    with open(pyFile, "r") as fp:
        line = fp.read()
        line = re.sub(r"[^']+'{1}[^']+", '"', line)
        line = re.sub(r'""".*"""', "", line)
        data = data + re.sub(r"\n(?!\"|')", "\r\n", line)
        print(line)

f = open('converted.py', 'wt')
f.write(repr(data))
#f.write((data))
f.close()
