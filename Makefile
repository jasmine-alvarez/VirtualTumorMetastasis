run:
	python2 3DTumorSimul_MultiRegionSeq.py 500 0.6 0.00001 0.1 0 
#         python2 3DTumorSimul_MultiRegionSeq.py 10 0.6 0.1 0.1 0 
#     python2 3DTumorSimul_MultiRegionSeq_test.py 10 0.6 0.1 0.1 0 
#         python2 3DTumorSimul_MultiRegionSeq_test.py 10 0.6 0.00001 0.1 0 
#         python2 3DTumorSimul_MultiRegionSeq.py 5000 0.6 0.00001 0.1 0 
	# Deme size, neural mutation rate, advantagous mutation rate, selection coefficience, replication

profile:
	python2 -m cProfile -s tottime 3DTumorSimul_MultiRegionSeq.py 500 0.6 0.1 0.1 0 


Sync:
	rsync -azP ./* pathology@ceserver:workdir/VirtualTumorEvolution/VirtualTumorEvolution
