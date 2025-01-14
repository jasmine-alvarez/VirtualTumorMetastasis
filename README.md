```
python2 with_mut_name.3DTumorSimulMetastasis.py 500 0.6 0.00001 0.01 1000000 1 0
```

# The README of Wenjie Sun's VirtualTumorMetastasis repo:

### VirtualTumorMetastasis
The script `3DTumorSimulMetastasis.py` simulates tumor growth and metastasis. It was adapted from Zheng Hu's [VirtualTumorEvolution](https://github.com/cancersysbio/VirtualTumorEvolution).

The output of the script includes the multi-region sequencing results of primary and metastatic lesions and high frequency mutations of each Deme in the cross section of the primary and metastatic lesions.

To run the script:
```
python2 3DTumorSimulMetastasis.py 5000 0.6 0.00001 0.01 1000000 1 0
				  | Deme size, the cell number of each deme.
				       | Mutation rate each cell duplication.
				           | Advantageous mutation rate each cell duplication.
					           | Selection coefficien for advantageous mutation.
						        | Primary tumor cell number when metastasis happen.
							        | Metastasis cell number
								  | Batch ID
```

# The README of Zheng Hu's VirtualTumorEvolution repo:

### VirtualTumorEvolution
A Python script to simulate 3D tumor growth and multi-region sequencing data 
via an agent-based model. Deme subdivision is assumed in order to model cell
mixing and spatial contraint
* Spatial model: peripheral growth

Author
---
* Zheng Hu in Curtis lab@Stanford
* Release Date: 2/23/2017


Requirements
---
Python packages: numpy,sys,math,random,collections,sets

Usage
---

* Simulation of a typical tumor (~10^9 cells) is computationally costly.  We suggest to run this script on HPC cluster. 
* The memory cost is also large, e.g. it costs about ~40G when the final_tumor_size = 10^9 and mut_rate = 0.6.

To run the script

	$ python 3DTumorSimul_MultiRegionSeq.py deme_size mut_rate adv_rate s_coef repl
	e.g., python 3DTumorSimul_MultiRegionSeq.py 5000 0.6 0.00001 0.1 0
