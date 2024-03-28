from graph_tool.all import Graph, graph_draw, draw_hierarchy
import itertools

def build_nodes(announcements, artists):
    g = Graph(directed=False)
    artist_to_vertex = {}
    for announcement in announcements.values():
        announcement_artists = announcement['artists']
        for artist in artists:
            if artist not in artist_to_vertex:
                v = g.add_vertex()
                artist_to_vertex[artist] = v
    artist_name = g.new_vertex_property("string")
    for artist, v in artist_to_vertex.items():
        artist_name[v] = artist
    g.vertex_properties["artist_name"] = artist_name
    return g, artist_to_vertex

def build_edges(g, artist_to_vertex, announcements):
    import itertools
    edge_weights = {}
    for announcement in announcements.values():
        artists_ = announcement['artists']
        for artist1, artist2 in itertools.combinations(artists_, 2):
            edge = g.edge(artist_to_vertex[artist1], artist_to_vertex[artist2])
            if edge:
                edge_weights[edge] += 1
            else:
                edge = g.add_edge(artist_to_vertex[artist1], artist_to_vertex[artist2])
                edge_weights[edge] = 1
    weight = g.new_edge_property("int")
    for edge, weight_value in edge_weights.items():
        weight[edge] = weight_value
    g.edge_properties["weight"] = weight
    return g

def create_graph(announcements, artists):
    g, artist_to_vertex = build_nodes(announcements, artists)
    g = build_edges(g, artist_to_vertex, announcements)
    return g, artist_to_vertex


def create_subgraph_from_names(g, names, name_to_vertex):
    g_sub = Graph(directed=False)
    #For the new graph, new name-vertex mapping
    name_to_new_vertex = {}

    #Vertices: names
    name_property = g_sub.new_vertex_property("string")    
    for name in names:
        if name in name_to_vertex:
            v = g_sub.add_vertex()
            name_property[v] = name
            name_to_new_vertex[name] = v  # Map the name to the new vertex

    g_sub.vertex_properties["name"] = name_property

    #Edges: connection counts
    edge_weights = g_sub.new_edge_property("int")
    for name1, name2 in itertools.combinations(names, 2): #pairwise combinations, cleaner than double loop
        #Check if the edge already exists
        if name1 in name_to_vertex and name2 in name_to_vertex: #Not necessary on paper, but I had some issues sometimes with obscurely created (sub)graphs
            edge = g.edge(name_to_vertex[name1], name_to_vertex[name2])
            if edge:
                edge_sub = g_sub.add_edge(name_to_new_vertex[name1], name_to_new_vertex[name2])
                edge_weights[edge_sub] = g.edge_properties["weight"][edge]

    g_sub.edge_properties["weight"] = edge_weights

    return g_sub

def create_subgraph_from_edges(g, edges):
    # Create a new graph
    g_sub = Graph(directed=False)

    # Create a dictionary to map names to new vertices
    name_to_new_vertex = {}

    # Create a vertex property map for the names
    name_property = g_sub.new_vertex_property("string")

    # Add vertices to the new graph
    for edge in edges:
        name1 = g.vertex_properties["artist_name"][edge.source()]
        name2 = g.vertex_properties["artist_name"][edge.target()]
        if name1 not in name_to_new_vertex:
            v1 = g_sub.add_vertex()
            name_property[v1] = name1
            name_to_new_vertex[name1] = v1  # Map the name to the new vertex
        if name2 not in name_to_new_vertex:
            v2 = g_sub.add_vertex()
            name_property[v2] = name2
            name_to_new_vertex[name2] = v2  # Map the name to the new vertex

    g_sub.vertex_properties["name"] = name_property

    # Create an edge property map for the weights
    edge_weights = g_sub.new_edge_property("int")

    for edge in edges:
        name1 = g.vertex_properties["artist_name"][edge.source()]
        name2 = g.vertex_properties["artist_name"][edge.target()]
        edge_sub = g_sub.add_edge(name_to_new_vertex[name1], name_to_new_vertex[name2])
        edge_weights[edge_sub] = g.edge_properties["weight"][edge]

    g_sub.edge_properties["weight"] = edge_weights

    return g_sub