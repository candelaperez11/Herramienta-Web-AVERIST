#from networkx.utils import generate_unique_node    # Deprecated
import uuid



#----------------------------------------------------------------------------------------------#
def negative_cycle(pred, node):
    
	""" Look for the cycle in a path containing node and having pred as the predecessor list. """
    
	path = []
	repetition = False
	
	while not repetition:
		node = pred[node]
		
		if node in path:
			repetition = True
			repeated_node = node
		
		path.append(node)
    
	# now it is computed the total weight of the cycle and the nodes included on that
	cycle = path[path.index(repeated_node):len(path)]
	cycle.reverse()
	
	return cycle



#*************************************************************************
#*** MODIFIED ALGORITHMS FROM NETWORKX PACKAGE IN ORDER TO USE PRODUCT ***
#*** INSTEAD OF SUM OF WEIGHTS					       ***
#*************************************************************************

def bellman_ford_product(G, source, weight = 'weight'):
    """Compute shortest path lengths and predecessors on shortest paths
        in weighted graphs, considering the total weight as the product of
        the weights involved.
        
        The algorithm has a running time of O(mn) where n is the number of
        nodes and m is the number of edges.  It is slower than Dijkstra but
        can handle negative edge weights.
        
        Parameters
        ----------
        G : NetworkX graph
        The algorithm works for all types of graphs, including directed
        graphs and multigraphs.
        
        source: node label
        Starting node for path
        
        weight: string, optional (default='weight')
        Edge data key corresponding to the edge weight
        
        Returns
        -------
        pred, dist : dictionaries
        Returns two dictionaries keyed by node to predecessor in the
        path and to the distance from the source respectively.
        
        Raises
        ------
        NetworkXUnbounded
        If the (di)graph contains a negative cost (di)cycle, the
        algorithm raises an exception to indicate the presence of the
        negative cost (di)cycle.  Note: any negative weight edge in an
        undirected graph is a negative cost cycle.
        
        Examples
        --------
        >>> import networkx as nx
        >>> G = nx.path_graph(5, create_using = nx.DiGraph())
        >>> pred, dist = nx.bellman_ford(G, 0)
        >>> pred
        {0: None, 1: 0, 2: 1, 3: 2, 4: 3}
        >>> dist
        {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}
        
        >>> from nose.tools import assert_raises
        >>> G = nx.cycle_graph(5, create_using = nx.DiGraph())
        >>> G[1][2]['weight'] = -7
        >>> assert_raises(nx.NetworkXUnbounded, nx.bellman_ford, G, 0)
        
        Notes
        -----
        Edge weight attributes must be numerical.
        Distances are calculated as sums of weighted edges traversed.
        
        The dictionaries returned only have keys for nodes reachable from
        the source.
        
        In the case where the (di)graph is not connected, if a component
        not containing the source contains a negative cost (di)cycle, it
        will not be detected.
        
        """
    if source not in G:
        raise KeyError("Node %s is not found in the graph"%source)
    numb_nodes = len(G)
    
    dist = {source: 1}
    pred = {source: None}
    
    neg_cycle = False
    node_in_path_with_cycle = source
	
    if numb_nodes == 1:
        return neg_cycle, pred, dist, node_in_path_with_cycle
    
    if G.is_multigraph():
        def get_weight(edge_dict):
            return max([eattr.get(weight,1) for eattr in edge_dict.values()])
    else:
        def get_weight(edge_dict):
            return edge_dict.get(weight,1)
    
    
    for i in range(numb_nodes):
        no_changes=True
        
        # Only need edges from nodes in dist b/c all others have dist==inf
        for u, dist_u in list(dist.items()): # get all edges from nodes in dist
            
            for v, edict in G[u].items():  # double loop handles undirected too
                
                
                dist_v = dist_u * get_weight(edict)
                
                
                if v not in dist or dist[v] < dist_v:
                    no_changes = False
                    neg_cycle_pred = pred
                    neg_cycle_dist = dist
                    if v in dist and dist[v] < dist_v:
                         node_in_path_with_cycle = v
                    dist[v] = dist_v
                    pred[v] = u

        if no_changes:
            break
    else:
        neg_cycle = True
        pred = neg_cycle_pred
        dist = neg_cycle_dist
    
    return neg_cycle, pred, dist, node_in_path_with_cycle

def greater_than_one_edge_cycle(G, weight = 'weight'):
    """Return True if there exists a cycle with weight greater than 1 anywhere in G.
        
        Parameters
        ----------
        G : NetworkX graph
        
        weight: string, optional (default='weight')
        Edge data key corresponding to the edge weight
        
        Returns
        -------
        negative_cycle : bool
        True if a negative edge cycle exists, otherwise False.
        
        Examples
        --------
        >>> import networkx as nx
        >>> G = nx.cycle_graph(5, create_using = nx.DiGraph())
        >>> print(nx.negative_edge_cycle(G))
        False
        >>> G[1][2]['weight'] = -7
        >>> print(nx.negative_edge_cycle(G))
        True
        
        Notes
        -----
        Edge weight attributes must be numerical.
        Distances are calculated as sums of weighted edges traversed.
        
        This algorithm uses bellman_ford() but finds negative cycles
        on any component by first adding a new node connected to
        every node, and starting bellman_ford on that node.  It then
        removes that extra node.
        """
    #newnode = generate_unique_node()   # Deprecated. Removed in NetworkX v3.0
    newnode = str(uuid.uuid4())

    G.add_edges_from([ (newnode,n) for n in G])
    
    stable, pred, dist, node = bellman_ford_product(G, newnode, weight)
    #    print 'pred = ', pred
    
    G.remove_node(newnode)
    
    return stable, pred, dist, node

#***********************************************************************
#*** MODIFIED BY MIRIAM **************************************** END ***
#***********************************************************************