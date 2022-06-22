import requests
import bz2
x = requests.get('https://cta-bus-and-train-tracker.s3.amazonaws.com/traintracker/rollup/2022-06-13.bz2').content
print(bz2.decompress(x))