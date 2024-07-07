from RStask import CountingFuncnction
model=CountingFuncnction('cpu')
txt='Remote-Sensing-ChatGPT-main/image/airport_1_jpg.rf.888faa9b857184ef83ae2a4068a39bc0.jpg,plane'
p,t=txt.split(",")
model.inference(p,t)
