#! /usr/bin/python

##
## USAGE:
##   This script is used to simulate sequencing data from paired primary and metastasis.
##
## REF:
##   The script is modified from https://github.com/cancersysbio/VirtualTumorEvolution.
##   Original Description:
##   ################################################################################
##   A Python script to simulate 3D tumor growth and multi-region sequencing data  ##
##   via an agent-based model. Deme subdivision is assumed in order to model cell  ##
##   mixing and spatial contraint.                                                 ##
##                                                                                 ##
##   Spatial model: pripheral growth                                               ##
##   Author: Zheng Hu in Curtis lab@Stanford                                       ##
##   Release Date: 2/20/2017                                                       ##
##   ################################################################################
##
## AUTHOR: 
##   Wenjie Sun, sunwjie@gmail.com 
##
## DATE:
##   4/14/2019


import sys,os,math,random
import numpy as np
from collections import Counter
import sets
import math
# New packages
import random
import string
import pickle

class deme():
    def __init__(self):
        self.present= 0         ## whether the deme is empty or occupied: 0-empty;1-occupied
        self.background = []    ## the background founder lineage after tumor tranformation
        self.advant = []        ## the advantageous cells

# New functions
def create_random_mut(current_id, mut_dict):
    """
    For each new mutation randomly select chr, position, ref, and alt alleles recorded in output file.
    """
    mut_dict[str(current_id)] = [random.choice(chr_dict.keys())]
    mut_dict[str(current_id)].append(chr_dict[mut_dict[str(current_id)][0]][0])
    mut_dict[str(current_id)].append(random.choice(range(chr_dict[mut_dict[str(current_id)][0]][1],chr_dict[mut_dict[str(current_id)][0]][2]+1)))
    mut_dict[str(current_id)].append(random.choice(list(set('ATCG'))))
    mut_dict[str(current_id)].append(random.choice(list(set('ATCG') - set(mut_dict[str(current_id)][3]))))

# Previous functions

def createLattice(d):
    """
    Create a 3D cubic lattice with side length of 2d+1 where each site contains a empty deme.
    """
    lattice = {}
    for x in range(0,2*d+1):
        for y in range(0,2*d+1):
            for z in range(0,2*d+1):
                lattice[(x,y,z)] = deme()
    return lattice

def neighbor26((a,b,c)): 
    """
    Moore neighbourhood: 26 neighbour sites of (a,b,c).
    Which was used in the 2017 Nature genetic paper.
    """
    neighbor = [(a-1, b-1, c-1),(a-1, b-1, c),(a-1, b-1, c+1),(a-1, b, c-1),(a-1, b, c),(a-1, b, c+1),(a-1, b+1, c-1),(a-1, b+1, c),(a-1, b+1, c+1),(a, b-1, c-1),(a, b-1, c),(a, b-1, c+1),(a, b, c-1),(a, b, c+1),(a, b+1, c-1),(a, b+1, c),(a, b+1, c+1),(a+1, b-1, c-1),(a+1, b-1, c),(a+1, b-1, c+1),(a+1, b, c-1),(a+1, b, c),(a+1, b, c+1),(a+1, b+1, c-1),(a+1, b+1, c),(a+1, b+1, c+1)]
    return neighbor

def neighbor6((a,b,c)):
    """
    von Neumann neighbourhood: 6 neighbour sites of (a,b,c).
    """
    neighbor = [(a-1, b, c),(a+1, b, c),(a, b-1, c),(a, b+1, c),(a, b, c-1),(a, b, c+1)]
    return neighbor

def localNeighbor((a,b,c),r):
    """
    A function to search the local neighbour sites of (a,b,c) within an area of radius r in the 3D cubic lattice.
    """
    neighbor = []
    for x in range(-r,r+1):
        for y in range(-r,r+1):
            for z in range(-r,r+1):
                if pow(x,2)+pow(y,2)+pow(z,2) < pow(r+1,2):
                    neighbor += [(a+x,b+y,c+z)]
    return neighbor

def traceLineage(mlineage,mutid):
    """
    A function to obtain the mutational lineage of a cell from the mutation id of the most recently occurred mutation in the cell. 
    For example, the input ID (most recently occurred mutation) of target cell is "100" and the output is "1-12-35-56-100", which is the mutation lineage of the cell
    
    mlineage - the list that could be used to recover the mutational lineage given the most recent mutation id of a lineage
    mutid - the mutation ID of the most recently occurred mutation in the cell
    """
    recent_muts = mutid.split(',')  # it is possible that multiple mutations occur during in a cell division. For instance, the mutation id of most recently occurred mutations is "100,101"
    recent_muts = [int(t) for t in recent_muts]
    first_mut = recent_muts[0]      # the first mutation id in a multi-mutation event
    trace = []
    while first_mut > 0:
        trace += recent_muts
        recent_muts = mlineage[first_mut].split(',')
        recent_muts = [int(t) for t in recent_muts]
        first_mut = recent_muts[0]
    return trace

    
def get_ceil(value): 
    """
    A function to choose the upper or lower integral value given a non-integral number
    """
    ceil_int = int(math.ceil(value))
    return ceil_int
#     lower_int = int(value)
#     upper_int = lower_int+1
#     if random.random() < value-lower_int:
#         return upper_int
#     else:
#         return lower_int


def initiateFirstDeme(maxsize,lineage,current_id):
    """
    The growth of the initial deme from a single transformed tumor cell via a random discrete-time birth-death process

    INPUT
    maxsize - size limit of a deme
    lineage - a list that stores the lineage information of mutations
    current_id - the starting mutation ID
    OUTPUT
    neu_list - neutral cell list
    adv_list - advantageous cell list
    current_id - 
    lineage -
    """
    neu_list = [str(current_id)]
    adv_list = []
    current_deme_size = 1
    while current_deme_size < maxsize:
        n1,n2 = len(neu_list),len(adv_list)                         
        #n1 and n2 are the current number of neutral founder cells and advantageous cells, respectively
        neu_divcells =  int(n1*birth_rate+1)                        
        #number of dividing cells of neutral lineage in this generation. The other cells will die in the next generation
        neu_list = random.sample(neu_list,neu_divcells)*2
        if n2 > 0:
            adv_divcells = get_ceil(n2*birth_rate*(1+s_coef))   
            #number of dividing cells of advantageous lineage in this generation        
            adv_list = random.sample(adv_list,adv_divcells)*2
        n1,n2 = len(neu_list),len(adv_list)
        current_deme_size = n1+n2
        if n1 > 0:
            new_mut1 = np.random.poisson(mut_rate*n1)               
            # the total number of mutations occurring in a generation follows Poission distribution with lambda=u*n
            mut_assig1 = Counter(np.random.choice(n1,new_mut1))
            for x1 in mut_assig1.keys():
                nmut = mut_assig1[x1]
                new_mut1 = range(current_id+1,current_id+1+nmut)
                mut_str = ",".join(map(str,new_mut1))
                #if nmut > 1:
                #    for t in new_mut1:
                #        multi_events[str(t)] = mut_str
                for xn in range(0,nmut):
                    current_id += 1
                    lineage += [neu_list[x1]]
                neu_list[x1] = mut_str
        if n2 > 0:
            new_mut2 = np.random.poisson(mut_rate*n2)
            mut_assig2 = Counter(np.random.choice(n2,new_mut2))
            for x2 in mut_assig2.keys():
                nmut = mut_assig2[x2]
                new_mut2 = range(current_id+1,current_id+1+nmut)
                mut_str = ",".join(map(str,new_mut2))
                #if nmut > 1:
                #    for t in new_mut2:
                #        multi_events[str(t)] = mut_str
                for xn in range(0,nmut):
                    current_id += 1
                    lineage += [adv_list[x2]]
                adv_list[x2] = mut_str
        
        if random.random() < adv_rate*n1:                           # occurence of advantageous mutation on the neutral lineage
            current_id += 1
            current_n1 = len(neu_list)
            lineage += [str(neu_list[current_n1-1])]
            adv_list += [str(current_id)]
            neu_list = neu_list[0:current_n1-1]
    
    return neu_list,adv_list,current_id,lineage


def demeGrowthFission(neu_list,adv_list,lineage,current_id,current_deme_number):
    """
    A function to simulate deme expansion and fission and keep track of the mutational lineages
    """
    current_deme_size = len(neu_list)+len(adv_list)
    while current_deme_size < 2*deme_size:                          #when the deme size doubles, it will split into two offspring demes
        n1,n2 = len(neu_list),len(adv_list)
        neu_divcells =  get_ceil(n1*birth_rate)                 #number of dividing cells in this generation
        neu_list = random.sample(neu_list,neu_divcells)*2
        
        if n2 > 0:
            adv_divcells =  get_ceil(n2*birth_rate*(1+s_coef))  #number of dividing cells in this generation
            adv_list = random.sample(adv_list,adv_divcells)*2
        n1,n2 = len(neu_list),len(adv_list)
        current_deme_size = n1+n2
        if current_deme_number < 5*pow(10,7)/deme_size:             #stop mutation occurring when the tumor size is larger than 5*10^7 cells. The reason is that late occuring mutations have very small chance to present at detectable frequency even under selection.
            if n1 > 0:
                new_mut1 = np.random.poisson(mut_rate*n1)
                mut_assig1 = Counter(np.random.choice(n1,new_mut1))
                for x1 in mut_assig1.keys():
                    nmut = mut_assig1[x1]
                    new_mut1 = range(current_id+1,current_id+1+nmut)
                    mut_str = ",".join(map(str,new_mut1))
                    #if nmut > 1:
                    #    for t in new_mut1:
                    #        multi_events[str(t)] = mut_str
                    for xn in range(0,nmut):
                        current_id += 1
                        lineage += [neu_list[x1]]
                    neu_list[x1] = mut_str
            if n2 > 0:
                new_mut2 = np.random.poisson(mut_rate*n2)
                mut_assig2 = Counter(np.random.choice(n2,new_mut2))
                for x2 in mut_assig2.keys():
                    nmut = mut_assig2[x2]
                    new_mut2 = range(current_id+1,current_id+1+nmut)
                    mut_str = ",".join(map(str,new_mut2))
                    #if nmut > 1:
                    #    for t in new_mut2:
                    #        multi_events[str(t)] = mut_str
                    for xn in range(0,nmut):
                        current_id += 1
                        lineage += [adv_list[x2]]
                    adv_list[x2] = mut_str
            
            if random.random() < adv_rate*n1:
                current_id += 1
                current_n1 = len(neu_list)
                lineage += [str(neu_list[current_n1-1])]
                adv_list += [str(current_id)]
                neu_list = neu_list[0:current_n1-1]
            #n1,n2 = len(neu_list),len(adv_list)
    random.shuffle(neu_list)
    if len(neu_list) > 0:
        offspring_neu = np.random.binomial(len(neu_list),0.5)       # the offpring deme size is determined by a Binomial distribution B(n,0.5)
    else:
        offspring_neu = 0
    neu_list1=neu_list[0:offspring_neu]
    neu_list2=neu_list[offspring_neu:len(neu_list)]
    random.shuffle(adv_list)
    if len(adv_list) > 0:
        offspring_adv = np.random.binomial(len(adv_list),0.5)
    else:
        offspring_adv = 0
    adv_list1=adv_list[0:offspring_adv]
    adv_list2=adv_list[offspring_adv:len(adv_list)]
    
    return neu_list1,neu_list2,adv_list1,adv_list2,current_id,lineage


def seqProcessing(sp,sample_keys,mlineage,size_par,mean_depth,purity):
    """
    Model the random sampling process in NGS and report the sequencing allele frequencies in a sample of cells
    
    sp- the lattice space
    sample_keys- the locations for the demes in a bulk sample
    size_par- variance parameter for negative-binomial distribution
    mean_depth- the mean depth of the sequencing
    purity- tumor purity
    """
    all_cur_id = []                                     # all most recently occurred mutations
    all_mut_id = []                                     # all mutations in the sampled cells
    for key in sample_keys:
        smuts = list(sp[key].background + sp[key].advant)
        all_cur_id += smuts
#     sample_size = 10000                                 # the number of cells for sequencing analysis
    sample_size = 100                                 # the number of cells for sequencing analysis
    sample_id = random.sample(all_cur_id,sample_size)
    id_count = Counter(sample_id)
    for x in id_count.keys():
        xlineage = traceLineage(mlineage,x)
        all_mut_id += xlineage*id_count[x]
    mut_count = Counter(all_mut_id)
    prob_par=size_par*1.0/(size_par+mean_depth)
    sampleAF = {}                                       # a dictionary storing the mutation IDs and corresponding depth and allele frequency the seq data
    for x in mut_count.keys():
        true_af = mut_count[x]*0.5*purity/sample_size   # the true allele frequency in the sample
        if true_af > 0.001:                             # filter mutations with very low frequency that is not detectable by ~100X sequencing depth
            site_depth = np.random.negative_binomial(size_par,prob_par)
            if site_depth >= 15:                        # seq depth cutoff for "calling" a mutation
                var_reads = np.random.binomial(site_depth,true_af)
                seq_af = var_reads*1.0/site_depth
                if var_reads >= 4:                      # variant reads cutof for "calling" a mutation
                    sampleAF[str(x)] = (site_depth,seq_af)
    return sampleAF

def highMuts(sp,position,mlineage,cutoff):
    """
    Obtain the high-frequency mutations (vaf>cutoff) in a particular deme
    
    sp - the lattice space
    position - the location of the deme
    mlineage - mutation lineage dictionary
    cutoff - the VAF cutoff for a "high-frequency" mutation, e.g. 0.4
    """
    all_cur_id = sp[position].background + sp[position].advant
    all_mut_id = []
    sample_size = 100
    sample_id = random.sample(all_cur_id,sample_size)
    id_count = Counter(sample_id)
    for y in id_count.keys():
        xlineage = traceLineage(mlineage,y)
        all_mut_id += xlineage*id_count[y]
    mut_count = Counter(all_mut_id)
    highAF_muts = []
    for x in mut_count.keys():
        allele_freq = mut_count[x]*1.0/sample_size
        if allele_freq > cutoff:
            highAF_muts += [x]
    return highAF_muts


def pubMutGenerator(n,size_par,mean_depth,purity):
    """
    A function to generate the public clonal mutations occured during the multi-step tumorigenesis before transformation.
    
    n- number of clonal mutations
    size_par- variation parameter in the negative binomial distribution
    mean_death- mean seq depth
    """
    prob_par=size_par*1.0/(size_par+mean_depth)
    mean_af = 0.5*purity
    depth_pub = []
    maf_pub = []
    for k in range(0,n):
        correct = 0
        while correct == 0:
            site_depth = np.random.negative_binomial(size_par,prob_par)
            if site_depth >= 15:
                correct =1
        var_reads = np.random.binomial(site_depth,mean_af)
        site_maf = var_reads*1.0/site_depth
        depth_pub += [site_depth]
        maf_pub += [site_maf]
    return depth_pub,maf_pub


def localSampling(region,sample_number,cutoff):
    """
    A function to sampling the locations of multiple bulk samples in a local region.
    """
    success = 0
    while success == 0:
        locations = random.sample(region,sample_number)
        repeat = sample_number*(sample_number-1)
        minall = 999
        for x in range(0,repeat):
            rs = random.sample(locations,2)
            min_distance = min([abs(rs[0][0]-rs[1][0]),abs(rs[0][1]-rs[1][1]),abs(rs[0][2]-rs[1][2])])
            if min_distance < minall:
                minall = min_distance
        if min_distance > 2*cutoff:
            success = 1
    return locations


def bulkTissueSampling(sp,location,radius):
    """
    A function to sampling a bulk sample in a local region.
    """
    local_region = localNeighbor(location,radius)
    bulk_tissue = []
    for x in local_region:
        if sp[x].present == 1:
            bulk_tissue += [x]
    return bulk_tissue


def lineageDashLink(mlist):
    """
    Transform the mutation lineage from list (e.g [1,3,10,20]) to dash-linked string (e.g. 1-3-10-20)
    """
    if len(mlist) > 0:
        dstring = str(mlist[0])
        for x in mlist[1:len(mlist)]:
            dstring += "-"
            dstring += str(x)
        return dstring
    else:
        return "0"
        
def missingDepth(vafdata,absent_muts,mean_depth):
    """
    Randomly generate the sequencing depth for the mutation-absent sites across samples
    """
    for x in absent_muts:
        done = 0
        while done == 0:
            missing_depth = np.random.negative_binomial(2,2.0/(2+mean_depth))
            if missing_depth >= 15:
                done = 1
        vafdata[str(x)] = (missing_depth,0)
    return vafdata

def get_periphery(space, current_keys):
    periphery = [] # the locations of periheral demes on tumor surface
    for key in current_keys:
        neikeys = neighbor26(key)
        for z in neikeys:
            if space[z].present == 0:
                periphery +=[key]
                break
    return periphery

def grow_tumor(first_neu, first_adv, mut_id, mutlineage, rd, final_deme_number, meta_init_primary_deme_size = 0, meta_cell_n = 0):   
    """
    Grow the tumor, if the meta_init_primary_deme_size == 0, no meta init
    """
    space = createLattice(rd)
    space[(rd,rd,rd)] = deme()                      #initiate the space with a empty deme in the center site (rd,rd,rd)
    space[(rd,rd,rd)].present = 1
    space[(rd,rd,rd)].background = list(first_neu)
    space[(rd,rd,rd)].advant = list(first_adv)
    current_keys = [(rd,rd,rd)]
    current_deme_number =1                                 #current deme number
    surface_keys = [(rd,rd,rd)]
    surface_deme_number =1
    deme_time_generation = 0
    sampled = False
    if (meta_init_primary_deme_size < 1): 
        sampled = True

    while current_deme_number < final_deme_number:
        print "current deme number: " + str(current_deme_number)
        new_keys = []
        for w in range(0,surface_deme_number):             # deme expansion occurs in the surface of a tumor
            ckey = random.choice(current_keys)
            if space[ckey].present == 1:
                rx,ry,rz = ckey[0],ckey[1],ckey[2]
                nei_sites = neighbor26((rx,ry,rz))  # neighbor sites of (rx,ry,rz)
                empty_sites = []                    # the empty neighbor sites
                for key in nei_sites:
                    if space[key].present == 0:
                        empty_sites += [key]
                if len(empty_sites) > 0:
                    rand_prob = random.random()
                    # the probability that a deme is chosen for expansion and split in a given step is proportional to the # of empty neighbor sites
                    if rand_prob < 1-math.exp(-len(empty_sites)*0.25): 
                        pre_neu = list(space[(rx,ry,rz)].background)
                        pre_advant = list(space[(rx,ry,rz)].advant)
                        post_neu1,post_neu2,post_adv1,post_adv2,mut_id,mutlineage = demeGrowthFission(pre_neu,pre_advant,mutlineage,mut_id,current_deme_number)
                        nextkey = random.choice(empty_sites)
                        space[ckey].background = list(post_neu1)
                        space[ckey].advant = list(post_adv1)
                        space[nextkey].background = list(post_neu2)
                        space[nextkey].advant = list(post_adv2)
                        space[nextkey].present = 1
                        current_keys += [nextkey]
                        current_deme_number += 1
                        new_keys += [nextkey]
        ###update surface###
        surface_update = list(surface_keys+new_keys)
        surface_keys = []
        for fkey in surface_update:
            neisites = neighbor26(fkey)
            random.shuffle(neisites)
            for key in neisites:
                if space[key].present == 0:
                    surface_keys += [fkey]
                    break
        surface_deme_number = len(surface_keys)
        current_deme_number = len(current_keys)
        deme_time_generation += 1  # plus 1 after generation
        if ((not sampled) and (current_deme_number >= meta_init_primary_deme_size or current_deme_number >= final_deme_number)):
            sampled = True
            meta_key = random.choice(surface_keys)
            meta_deme = deme()
            meta_deme.present = 1
            meta_deme_temp = space[meta_key]
            neu_n = len(meta_deme_temp.background)
            adv_n = len(meta_deme_temp.advant)
            meta_neu_n = int(math.ceil(float(meta_cell_n) / (neu_n + adv_n) * neu_n))
            meta_deme.background = list(np.random.choice(meta_deme_temp.background, meta_neu_n))
#             print(np.random.choice(meta_deme_temp.background, meta_neu_n))
            if (adv_n > 0):
                meta_advant_n = int(meta_cell_n - meta_neu_n)
                meta_deme.advant = list(np.random.choice(meta_deme_temp.advant, meta_advant_n))

    if (meta_init_primary_deme_size == 0):
        return space, current_keys, mut_id, mutlineage, current_deme_number, deme_time_generation
    else:
        return space, current_keys, mut_id, mutlineage, current_deme_number, deme_time_generation, meta_deme 

def write_maf(primary_periphery, meta_periphery, primary_space, meta_space, mutlineage, seq_depth, purity, file_name):
    """
    Sampleing 8 samples
    Surface demes in the eight quadrants
    For primary amd metastasis tumor, sample 4 quadrants respactively.
    """
    quadrant1,quadrant2,quadrant3,quadrant4,quadrant5,quadrant6,quadrant7,quadrant8 = [],[],[],[],[],[],[],[] 

    # Get the location key in the periphery
    for pky in primary_periphery:
        if pky[0] > rd and pky[1] > rd and pky[2] > rd:
            quadrant1 += [pky]
        if pky[0] < rd and pky[1] < rd and pky[2] < rd:
            quadrant2 += [pky]
        if pky[0] < rd and pky[1] > rd and pky[2] > rd:
            quadrant3 += [pky]
        if pky[0] > rd and pky[1] < rd and pky[2] < rd:
            quadrant4 += [pky]

    for pky in meta_periphery:
        if pky[0] > rd and pky[1] > rd and pky[2] < rd:
            quadrant5 += [pky]
        if pky[0] < rd and pky[1] < rd and pky[2] > rd:
            quadrant6 += [pky]
        if pky[0] > rd and pky[1] < rd and pky[2] > rd:
            quadrant7 += [pky]
        if pky[0] < rd and pky[1] > rd and pky[2] < rd:
            quadrant8 += [pky]

    # Print out the number of demes
#     print "# of demes in the periphery=",len(periphery)
#     print "# of demes in quadrant1=",len(quadrant1)
#     print "# of demes in quadrant2=",len(quadrant2)
#     print "# of demes in quadrant3=",len(quadrant3)
#     print "# of demes in quadrant4=",len(quadrant4)
#     print "# of demes in quadrant5=",len(quadrant5)
#     print "# of demes in quadrant6=",len(quadrant6)
#     print "# of demes in quadrant7=",len(quadrant7)
#     print "# of demes in quadrant8=",len(quadrant8)

    #p4samples = localSampling(quadrant1,8,1)
    # multisample == "8samples":
    locat1 = random.choice(quadrant1) # location of bulk tissue1
    locat2 = random.choice(quadrant2)
    locat3 = random.choice(quadrant3)
    locat4 = random.choice(quadrant4)

    locat5 = random.choice(quadrant5)
    locat6 = random.choice(quadrant6)
    locat7 = random.choice(quadrant7)
    locat8 = random.choice(quadrant8)

    sample8 = [locat1,locat2,locat3,locat4,locat5,locat6,locat7,locat8]

    tissue1 = bulkTissueSampling(primary_space,sample8[0],3)
    tissue2 = bulkTissueSampling(primary_space,sample8[1],3)
    tissue3 = bulkTissueSampling(primary_space,sample8[2],3)
    tissue4 = bulkTissueSampling(primary_space,sample8[3],3)

    tissue5 = bulkTissueSampling(meta_space,sample8[4],3)
    tissue6 = bulkTissueSampling(meta_space,sample8[5],3)
    tissue7 = bulkTissueSampling(meta_space,sample8[6],3)
    tissue8 = bulkTissueSampling(meta_space,sample8[7],3)
    print "Average # of demes in the 8 bulks",(len(tissue1)+len(tissue2)+len(tissue3)+len(tissue4)+len(tissue5)+len(tissue6)+len(tissue7)+len(tissue8))/8

    maf1 = seqProcessing(primary_space,tissue1,mutlineage,2,seq_depth,1)
    maf2 = seqProcessing(primary_space,tissue2,mutlineage,2,seq_depth,1)
    maf3 = seqProcessing(primary_space,tissue3,mutlineage,2,seq_depth,1)
    maf4 = seqProcessing(primary_space,tissue4,mutlineage,2,seq_depth,1)

    maf5 = seqProcessing(meta_space,tissue5,mutlineage,2,seq_depth,1)
    maf6 = seqProcessing(meta_space,tissue6,mutlineage,2,seq_depth,1)
    maf7 = seqProcessing(meta_space,tissue7,mutlineage,2,seq_depth,1)
    maf8 = seqProcessing(meta_space,tissue8,mutlineage,2,seq_depth,1)

    MAF_file = open(file_name, "w")
    MAF_file.write("gene"+" "+"chr"+" "+"pos"+" "+"ref"+" "+"alt"+" "+"public"+" "+"mean_depth"+" "+"mean_maf"+" "+"depth1"+" "+"maf1"+" "+"depth2"+" "+"maf2"+" "+"depth3"+" "+"maf3"+" "+"depth4"+" "+"maf4"+" "+"depth5"+" "+"maf5"+" "+"depth6"+" "+"maf6"+" "+"depth7"+" "+"maf7"+" "+"depth8"+" "+"maf8")
    MAF_file.write("\n")

    for k in range(0,npub):
        # Generate the public clonal mutations occured during the multi-step tumorigenesis before transformation
        pdepth,pmaf = pubMutGenerator(8,2,seq_depth, purity)
        # add mutation to mut dict
        create_random_mut(str(k), pub_dict)
        # write to output file
        MAF_file.write(str(pub_dict[str(k)][0])+" "+str(pub_dict[str(k)][1])+" "+str(pub_dict[str(k)][2])+" "+str(pub_dict[str(k)][3])+" "+str(pub_dict[str(k)][4])+" "+"1"+" "+str(np.mean(pdepth))+" "+str(np.mean(pmaf))+" "+str(pdepth[0])+" "+str(pmaf[0])+" "+str(pdepth[1])+" "+str(pmaf[1])+" "+str(pdepth[2])+" "+str(pmaf[2])+" "+str(pdepth[3])+" "+str(pmaf[3])+" "+str(pdepth[4])+" "+str(pmaf[4])+" "+str(pdepth[5])+" "+str(pmaf[5])+" "+str(pdepth[6])+" "+str(pmaf[6])+" "+str(pdepth[7])+" "+str(pmaf[7]))
        MAF_file.write("\n")

    muts_all = sets.Set(maf1.keys()) | sets.Set(maf2.keys()) | sets.Set(maf3.keys()) | sets.Set(maf4.keys()) |sets.Set(maf5.keys()) | sets.Set(maf6.keys()) |sets.Set(maf7.keys()) | sets.Set(maf8.keys())

    absent1 = muts_all-sets.Set(maf1.keys())
    absent2 = muts_all-sets.Set(maf2.keys())
    absent3 = muts_all-sets.Set(maf3.keys())
    absent4 = muts_all-sets.Set(maf4.keys())

    absent5 = muts_all-sets.Set(maf5.keys())
    absent6 = muts_all-sets.Set(maf6.keys())
    absent7 = muts_all-sets.Set(maf7.keys())
    absent8 = muts_all-sets.Set(maf8.keys())

    maf1 = missingDepth(maf1,absent1,seq_depth)
    maf2 = missingDepth(maf2,absent2,seq_depth)
    maf3 = missingDepth(maf3,absent3,seq_depth)
    maf4 = missingDepth(maf4,absent4,seq_depth)
    
    maf5 = missingDepth(maf5,absent5,seq_depth)
    maf6 = missingDepth(maf6,absent6,seq_depth)
    maf7 = missingDepth(maf7,absent7,seq_depth)
    maf8 = missingDepth(maf8,absent8,seq_depth)

    for mt in list(muts_all):
        # add mutation to mut dict
        create_random_mut(str(mt), pvt_dict)
        # write to output file
        MAF_file.write(str(pvt_dict[str(mt)][0])+" "+str(pvt_dict[str(mt)][1])+" "+str(pvt_dict[str(mt)][2])+" "+str(pvt_dict[str(mt)][3])+" "+str(pvt_dict[str(mt)][4])+" "+"0"+" "+str(np.mean([maf1[mt][0], maf2[mt][0], maf3[mt][0], maf4[mt][0], maf5[mt][0], maf6[mt][0], maf7[mt][0], maf8[mt][0]]))+" "+str(np.mean([maf1[mt][1], maf2[mt][1], maf3[mt][1], maf4[mt][1], maf5[mt][1], maf6[mt][1], maf7[mt][1], maf8[mt][1]]))+" "+str(maf1[mt][0])+" "+str(maf1[mt][1])+" "+str(maf2[mt][0])+" "+str(maf2[mt][1])+" "+str(maf3[mt][0])+" "+str(maf3[mt][1])+" "+str(maf4[mt][0])+" "+str(maf4[mt][1])+" "+str(maf5[mt][0])+" "+str(maf5[mt][1])+" "+str(maf6[mt][0])+" "+str(maf6[mt][1])+" "+str(maf7[mt][0])+" "+str(maf7[mt][1])+" "+str(maf8[mt][0])+" "+str(maf8[mt][1]))
        MAF_file.write("\n")
    MAF_file.close()

############# Main script to simulate a tumor and multi-region sequencing data #########
### Parameter intiation ###
deme_size = int(sys.argv[1])        # the deme size
mut_rate = float(sys.argv[2])       # the neutral mutation rate at whole exonic region
adv_rate = float(sys.argv[3])       # the advantageous mutation rate at each cell generation
s_coef = float(sys.argv[4])         # the selection coefficient
meta_init_primary_size = int(sys.argv[5])         # metastasis time
meta_cell_n = int(sys.argv[6])
repl = int(sys.argv[7])             # replication of simulation

purity = 1                          # Tumor purity
rd = 60                             # the side length of the 3D space
meta_init_primary_deme_size = meta_init_primary_size/deme_size # The deme size of primary when metastasis happend
#final_tumor_size = pow(10,9)        # the number of cells in the final tumor
final_tumor_size = pow(10,5)        # the number of cells in the final tumor
final_deme_number = final_tumor_size/deme_size    # the final number of demes in the tumor
birth_rate = 0.55                   # the birth probability at each cell generation during tumor growth
npub=100                            # the number of public mutation to be generated
seq_depth=50                       # the average sequencing depth
percentage = int(s_coef*100)        # the percentage form of the selection

mut_id = 0
mutlineage = ['0']                  # the lineage tracer
######################################################################################
# New step - init dict that will map mut_id keys to mutation names
with open('data/COSMIC_CGC.somatic.dict', 'rb') as f:
    chr_dict = pickle.load(f)
pub_dict, pvt_dict = {}, {}

## Primary Tumor
# The growth of the fisrt deme from single transformed cell
first_neu,first_adv,mut_id,mutlineage = initiateFirstDeme(deme_size,mutlineage,mut_id)  

# Grow
primary_space, current_keys, mut_id, mutlineage, current_deme_number, deme_time_generation, meta_deme = grow_tumor(first_neu, first_adv, mut_id, mutlineage, rd, final_deme_number, meta_init_primary_deme_size, meta_cell_n)

# Get periphery locations
primary_periphery = get_periphery(primary_space, current_keys)

## Metastasis Tumor
# Prepare metastasis cells
meta_first_neu = meta_deme.background 
meta_first_adv = meta_deme.advant 

# Grow
meta_space, meta_current_keys, mut_id, mutlineage, meta_current_deme_number, meta_deme_time_generation = grow_tumor(meta_first_neu, meta_first_adv, mut_id, mutlineage, rd, final_deme_number)

# Get periphery locations 
meta_periphery = get_periphery(meta_space, meta_current_keys)

# Output
output_filename = "simulMRS_deme"+str(deme_size)+"_s"+str(percentage)+"percent_8samples_u"+str(mut_rate)+"_"+str(repl)+"meta_init"+str(meta_init_primary_size)+"meta_cell_n"+str(meta_cell_n)+"depth"+str(seq_depth)+".txt"
write_maf(primary_periphery, meta_periphery, primary_space, meta_space, mutlineage, seq_depth, purity, output_filename)


####visulization of spatial clonal structure in the central plane###
## For primary tumor
central_plane = []
for key in current_keys:
    if key[2] == rd:
        central_plane += [key]

print "# of demes on the central plane=",len(central_plane)
primary_map_file = open("CloneMap3D_peri_u"+str(deme_size)+"_s"+str(percentage)+"percent_8samples_u"+str(mut_rate)+"_"+str(repl)+"meta_init"+str(meta_init_primary_size)+"meta_cell_n"+str(meta_cell_n)+"depth"+str(seq_depth)+"_primary.txt", "w")
primary_map_file.write("x"+" "+"y"+" "+"z"+" "+"lineage")
primary_map_file.write("\n")
for key in central_plane:
    cur_muts = highMuts(primary_space,key,mutlineage,0.4)
    cur_lineage = lineageDashLink(sorted(cur_muts))
    primary_map_file.write(str(key[0])+" "+str(key[1])+" "+str(key[2])+" "+str(cur_lineage))
    primary_map_file.write("\n")
primary_map_file.close()

## For metastasis tumor
central_plane = []
for key in meta_current_keys:
    if key[2] == rd:
        central_plane += [key]

print "# of demes on the central plane=",len(central_plane)
meta_map_file = open("CloneMap3D_peri_u"+str(deme_size)+"_s"+str(percentage)+"percent_8samples_u"+str(mut_rate)+"_"+str(repl)+"meta_init"+str(meta_init_primary_size)+"meta_cell_n"+str(meta_cell_n)+"depth"+str(seq_depth)+"_metastasis_.txt", "w")
meta_map_file.write("x"+" "+"y"+" "+"z"+" "+"lineage")
meta_map_file.write("\n")
for key in central_plane:
    cur_muts = highMuts(meta_space,key,mutlineage,0.4)
    cur_lineage = lineageDashLink(sorted(cur_muts))
    meta_map_file.write(str(key[0])+" "+str(key[1])+" "+str(key[2])+" "+str(cur_lineage))
    meta_map_file.write("\n")
meta_map_file.close()
