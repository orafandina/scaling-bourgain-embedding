# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 12:28:08 2022

@author: Ora Fandina
"""

import numpy as np
import math 
import sys
""" 
Implements Δ-bounded random partitions, as described in[ABN08]. 
A partition consists of a collection of clusters of type Cluster.

==========
Parameters

         Delta int:  describes the diameter of the partition (denoted Δ in the paper) 

"""


""" 
Implements a cluster of the partitions. 
A cluster contains points, which are ints from {0,n-1}.


    ===========
    Fileds


          cluster_index int: index of the cluster
          
          center int: center point of the cluster 
          
          radius double: radius of the cluster
          
          growth_rate double: uniform growth rate, defined as in the paper
          
          points numpy array: points that belong to the cluster

  """

class Cluster:
  def __init__(self, cluster_index=-1, center=-1, radius=-1, growth_rate=-1, points=None): 
      
  
      
    # when cluster is created, its sigma and ksi valuses are uniformly assinged
    # ksi is set to 1 iff growth rate of the center >= 2; the eta value is set accordignly

    self.cluster_index=cluster_index
    self.center=center
    self.radius=radius
    self.points=points 
    self.sigma=np.random.choice(2)  # {1,0} with uniform probab.
    self.hat_gr=max(growth_rate,2)
    self.ksi=int((growth_rate >= 2))
    self.eta=(1/256)*math.log(self.hat_gr, 2) #defined as in lecture notes, with delat=1/2, and constants as in the lecture notes
    

  def add_points(self, points_array):
    self.points=points_array.copy() #creates a new memory for the array and copies the values of the input

  def print_cluster_info(self):
    print('Cluster: ', self.cluster_index, 'Center point:', self.center, 'Radius:', self.radius, 'Sigma value:', self.sigma, 'Ksi value:', self.ksi, 'Eta value:', self.eta, 'Points:', self.points)  
     

""" 
Implements a process of randomly partitioning a given metric space. 
The resulting partition is Delta bounded, for a fixed Delta, passed as a parameter.


===========
Fileds

      input_metric numpy array: metric to partition, given by the matrix of pairwise distances
      
      diameter double: diameter of the input metric space, i.e., the largest distances between any two points in the space
      
      Delta double: diamter of the resulting clusters in the partition
      
      clusters_indeces numpy arrray: an arry of integers with values in {0, #number of clusters}, of length n - size of the input space.
                                     clusters_indeces[j] stores the index of the cluster x_j beongs to                                         
      
      partition_clusters Cluster array: the array of clusters generated by the random partition.
                                         partition_clusters[j] contains Cluster_j
          
"""    
    

class Uniform_Partition:
  def __init__(self, input_metric, Delta, Gamma=64):
    self.input_metric=input_metric 
    self.diameter=np.amax(self.input_metric)
    self.Delta=Delta
    self.Gamma=Gamma
    self.metric_size=len(input_metric)
    self.sorted_metric=np.sort(input_metric) 
    #cretaes a copy (new memory), with each row being sorted
    #so for each metric point x_j it is fast to compute all the points within certain distance from it
    
    self.metric_points=np.zeros(self.metric_size)
    
    self.clusters_indeces=np.zeros(self.metric_size)
    
    self.partition_clusters=[] #the list of Clusters generated during the process; empty at the init
    
    empty_cluster=Cluster()
    
    for i in range(self.metric_size):
      self.partition_clusters.append(empty_cluster)
    
    #the number of clusters in partition
    self.num_of_clusters=0
 
 
 
  def growth_rate(self, point: int, radius:float): 
      
    """ The point is represented by an index in {0, 1, ..., n-1}. Computes its growth rate (without taking max 2). """
      
    if(point > self.metric_size-1):
      sys.exit("Index of the point is out of the range");
    upper_radius=self.Gamma*radius;
    lower_radius=radius/self.Gamma
    num_points=np.searchsorted(self.sorted_metric[point], np.array([upper_radius,lower_radius]),side='right')
    gr_rate=num_points[0]/num_points[1]
    return(gr_rate)
  
    
  
  def pick_radius(self, Xi):
      
    """ Picking a randm radius from the following distr: 
        the real interval [Delta/4, Delta/2] is divided into intervals of length Delta/(8 log Xi).
        Where Xi will be set as hat_growth_rate of te point that minimizes it, and we round Xi to the nearest power of 2.
        An interval #l is then chosen with probability (1/2)^l, 
        except the last interval, which is chosen with prob. 2/(Xi)^2, such that the total probab. mass==1 . """  
    power_Xi=pow(2,math.ceil(math.log(math.ceil(Xi),2)))
    number_intervals=int(2*math.log(power_Xi,2))
    intervals_to_pick=np.arange(1,number_intervals+1)
    probabilities=np.fromfunction(lambda i: pow(1/2,i+1), (number_intervals, ))   
    probabilities[number_intervals-1]=2/(pow((power_Xi),2)) #the last interval is picked with a different probability than all the rest, i.e. with prob. 2/(Xi)^2
    chosen_interval=np.random.choice(intervals_to_pick, p=probabilities) #the interval to pick the radius from uniformly
    radius=np.random.uniform(self.Delta/4 +(chosen_interval-1)*(self.Delta/(8*math.log(power_Xi, 2))), self.Delta/4 +(chosen_interval)*(self.Delta/(8*math.log(power_Xi, 2))))
    return(radius)
    


  def generate_partition(self):
      
    """ Random partition generator. Geneartes a random partition of a given metric sapce, according to algortihm described in ABN[06].  """  
    #creates the list of all the points in the metric space that are still not covered by the partition
    points_to_cover=np.full((self.metric_size,), True) #all the points need to be covered by partition. When points_to_cover[j]==False, the point is already covered
    length=len(points_to_cover)
    hat_growth_rates=np.zeros(length) #growth rates of all the points that are still not covered by partition
    growth_rates=np.zeros(length)
    MAX=2*self.metric_size  #growth rate is always <= metric size

    for i in range(length):
        growth_rates[i]=self.growth_rate(i, self.Delta) #growth rates, without taking the max with 2
    hat_growth_rates=np.maximum(growth_rates, np.full(length,2)) #taking max with 2 at each entry
    
    cluster_index=-1
    
    while(length>0):
      
      
      cluster_index=cluster_index+1 #we are going to crteate a new cluster # cluster_index (starting from 0). Center point and all the metric points in this cluster will be assigned with this index.
      center=np.argmin(hat_growth_rates) #index of the next center: the point with the min hat growth rate 
      center_gr=growth_rates[center]
      center_hat_gr=hat_growth_rates[center] #the value of the hat growth rate of the min point
      radius=self.pick_radius(center_hat_gr) #picks a random radius with the relevant growth rate
      
      cluster=Cluster(cluster_index, center, radius, center_gr) #creates the cluster with this center and the chosen radius. Still don't have all the points in this cluster
      
      #the metric point with index "center" belongs to cluster with index  "cluster index"
      self.clusters_indeces[center]=cluster_index 

      #adds all the points that belong to this cluster, and removes them from the points to cover 
      
      points_in_cluster=np.flatnonzero(self.input_metric[center]<=radius) # Outputs all the indexes i with arr[i <= radius] (including the center point itself). 
                                                                          # These are the points that POTENTIALLY belong to the cluster. 
      
      true_cluster_points=[]
      for k in range(len(points_in_cluster)):
        if(points_to_cover[points_in_cluster[k]]==True):
          true_cluster_points.append(points_in_cluster[k])
          points_to_cover[points_in_cluster[k]]=False  #remove these points from points to cover
      array_points_in_cluster=np.array(true_cluster_points)
     
      num_of_points_in_cluster=len(array_points_in_cluster)
      
      # update the length: the number of points that are still to be covered
      length=length-num_of_points_in_cluster
      # adding the points to the cluster
      cluster.add_points(array_points_in_cluster)
      
      #assing to the points in cluster the index of cluster they belong to (cluster_index)
      for j in range(len(array_points_in_cluster)):
        self.clusters_indeces[array_points_in_cluster[j]]=cluster_index


      #It remains to add this newly generated cluster into the arry of clusters
      self.partition_clusters[cluster_index]=cluster

      #The last thing to do, is to take out of consideration the point with the min growth rate. 
      #We just assign the max value to all the growth rates of the points that already covered, and thus they will not be chosen as new centers.
      
      np.put(hat_growth_rates, array_points_in_cluster, MAX)
    self.num_of_clusters=cluster_index+1
  
    
  
  #TESTING FUNCTIONS
  def print_partition(self):
    print('Partition has', self.num_of_clusters, 'clusters')
    print('The partition contains following clusters:')
    for i in range(self.num_of_clusters):
       self.partition_clusters[i].print_cluster_info()
    print("Indeces of clusters:", self.clusters_indeces)   

 
  def embed_point(self, point: int):
    """ Embedding one point based on the given $\Delta$-bounded partition. We will run it #$log \Phi$ times, for all the scales of $\Delta$, and then sum up the results to obtain 1 final coordinate of the embedding.
     To get the embedding of a point into D coordinates sample D independed coordinates as above, and normalize the resulted vector by D^1/p.
     """  
    
    #This is the 'scalig' version of the embedding, i.e., takes min between the unscaled definition of embedding and Delta_i 
    cluster_of_point_indx=int(self.clusters_indeces[point])
    cluster=self.partition_clusters[cluster_of_point_indx]
    points_in_cluster=cluster.points
    
    #Computes the distance from x to the outside of its cluster. Namely, the dist from x to the closest point in X/points in cluster of x
    points_outside_cluster=np.delete(self.input_metric[point], points_in_cluster)
    if (len(points_outside_cluster)==0): 
      #sys.exit('A cluster in partition contains all points in the space. The input space is not a metric.')
      print('Warning: A cluster in partition contains all points in the space. The input space is not a metric.')
      dist_to_outside=np.amax(self.input_metric[point])
    else:
      dist_to_outside=np.amin(points_outside_cluster)

    coordinate=min(self.Delta, cluster.sigma*cluster.ksi*(1/cluster.eta)*dist_to_outside)
    return coordinate


class Embeding:
  
  """ Implements the Scaling Bourgain embedding as suggested in ABN[06]. 
      The instance is initialized with the metric space to be embedded, given by the matrix of disatnces. 
      The method fit(D, p) is then called with the number of dimensions to embed into D, and p is the rank of the l_p space to embed into.
      The method returns the matrix of vectors embedded in l_p^(D), in the columns of the matrix.
     
  ========
  Methods

         fit (Dimensions, p)
  
  
  """
  
  def __init__(self, input_metric): 
      
    """ Initializes an instance of embedding, with the metric space to embed. 
    The inout_metric is the disatnce matrix of the metric space. """  
    self.input_metric=input_metric
    self.metric_size=len(input_metric)
    self.diameter=np.amax(self.input_metric)
    self.min_dist=np.amin(self.input_metric[self.input_metric!=0])
    
  def fit(self, D:int, p:float): #D number of dimensions to embed into; p - l_p spae to embed into 
    embedded_vectors=np.zeros((D, self.metric_size)) # embedded vectors are in  the columns of the matrix
    for t in range(D):
      coordinates_array=np.zeros((self.metric_size,))
      for i in range(int(math.log(self.diameter/self.min_dist, 2))+1):
        partit=Uniform_Partition(self.input_metric, (self.diameter)/(2**(i+1)))
        partit.generate_partition()
        for j in range(self.metric_size):
          coordinates_array[j]=coordinates_array[j]+partit.embed_point(j)
      np.copyto(embedded_vectors[t], coordinates_array)
    return(embedded_vectors*(1/D**(1/p)))      

      

      
    

