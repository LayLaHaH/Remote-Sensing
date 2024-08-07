from RStask import LanduseFunction
model=LanduseFunction('cpu')
model.inference('./image/airport_1_jpg.rf.3c38a93e805e111768dd2e37658c7c75.jpg','road','outputLUS.png')