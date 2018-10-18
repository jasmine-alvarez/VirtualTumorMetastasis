run:
	python2 3DTumorSimul_MultiRegionSeq.py 5000 0.6 0.00001 0.1 100000000 0 
	python2 3DTumorSimul_MultiRegionSeq.py 5000 0.6 0.00001 0.1 10000 0 
#         Deme size, neural mutation rate, advantagous mutation rate, selection coefficience, metastasis initiate time(primary tumor size),replication
#         python2 3DTumorSimul_MultiRegionSeq.py 500 0.6 0.00001 0.2 0 

profile:
	python2 -m cProfile -s tottime 3DTumorSimul_MultiRegionSeq.py 500 0.6 0.1 0.1 0 


Sync:
	rsync -azP ./* pathology@ceserver:workdir/VirtualTumorEvolution/VirtualTumorEvolution
