import dash
import dash_cytoscape as cyto
from dash import html, Input, Output, State, no_update
import numpy as np
import random
from pathlib import Path
import os

from animeinfo import AnimeInfo

NX_INIT = 10 # 初期ノードのx数
NY_INIT = 10 # 初期ノードのy数
DELTA_INIT = 250 # 初期ノードの間隔
N_NEW_NODE = 3 # クリック時に追加するノード数
LENGTH_EDGE = 180 # クリック時に追加するノードの距離
ANGLE_NEW_NODE = np.pi/3.5 # クリック時に追加するノードの角度
SIZE_NODE = 75 # ノードのサイズ
IS_DEBUG = bool(os.getenv("IS_DEBUG", True))

def init_page():
    nodes_id = random.choices([path.stem for path in Path("data/node_anime/").glob("*.json")], k=NX_INIT*NY_INIT)
    nodes = {
        node_id: [
            AnimeInfo(node_id),
            DELTA_INIT/2*(i%2-0.5)+DELTA_INIT*(i//NX_INIT-NX_INIT/2),
            DELTA_INIT*(i%NY_INIT-NY_INIT/2)
        ]
        for i,node_id
        in enumerate(nodes_id)
    }
    edges = []
    return nodes, edges

cyto.load_extra_layouts()
app = dash.Dash(__name__)
app.config.prevent_initial_callbacks = 'initial_duplicate'
nodes, edges = init_page()

def create_tree_elements(nodes, edges):
    elements = []
    for node_id, node in nodes.items():
        info, x, y = node
        imageURL = info.imageURL
        element = {
            'data': {
                'id': node_id,
                'label': info.title,
                'image': imageURL,
                'bgcolor': info.bgcolor,
                'opacity': info.opacity
            },
            'position': {
                'x': x,
                'y': y
            }
        }
        elements.append(element)
    for edge in edges:
        source, target, label = edge
        element = {
            'data': {
                'source': source,
                'target': target,
                'label': label,
            }
        }
        elements.append(element)
    return elements

cytoscape = cyto.Cytoscape(
    id='tree-graph',
    elements=create_tree_elements(nodes, edges),
    style={'width': '100%', 'height': '100vh', 'display': 'inline-block'},
    layout={
        'name': 'preset',
        'fit': False,
        'padding': 0,
        'animate': False,
    },
    responsive=True,
    zoomingEnabled=True,
    userZoomingEnabled=True,
    zoom=1,
    minZoom=0.1,
    maxZoom=10,
    wheelSensitivity=0.1,
    stylesheet=[
        {
            'selector': 'node',
            'style': {
                'background-image': 'data(image)',
                'background-fit': 'cover',
                'width': f'{SIZE_NODE}px',
                'height': f'{SIZE_NODE}px',
                'label': 'data(label)',
                'text-valign': 'center',
                'color': 'white',
                'font-size': '10px',
                'text-outline-width': 2,
                'text-outline-color': '#000',
                'background-color': 'data(bgcolor)',
                'text-wrap': 'wrap',
                'text-max-width': '100px',
                'text-overflow-wrap': 'break-word',
                'text-overflow': 'ellipsis',
                'opacity': 'data(opacity)',
            }
        },
        {
            'selector': 'edge',
            'style': {
                'width': 2,
                'line-color': '#ccc',
                'label': 'data(label)',
                'font-size': '8px',
                'text-rotation': 'autorotate',
                'text-margin-y': '-10px',
                'text-outline-width': 0,
                'text-outline-color': 'transparent',
                'text-background-padding': '2px',
                'text-background-shape': 'roundrectangle',
                'text-background-padding-relative-to': 'none',
            }
        },
    ]
)

app.layout = html.Div([
    html.Button('Reset', id='submit-val', n_clicks=0),
    cytoscape,
    html.Div([], id='sidebar', style={'width': '25%', 'display': 'inline-block', 'vertical-align': 'top', 'padding': '0px'})
], id='overlay-container')

# ############################## CALLBACKS ####################################

@app.callback(
    Output('sidebar', 'children'),
    [Input('tree-graph', 'mouseoverNodeData')],
)
def update_sidebar(nodeData):
    if not nodeData:
        content = html.Div([html.H2("気になるアニメをクリックしてください"), html.P("ここには補足情報が表示されます")])
        img = None
        bgcolor = '#0b3d7e'
    else:
        node_id = nodeData['id']
        if node_id not in nodes:
            return no_update
        info = nodes[node_id][0]
        img = info.imageURL
        bgcolor = info.bgcolor
        content = []
        content.append(html.H2(info.title))
        content.extend([html.P(i) for i in info.description.split("\n")])
    if img:
        return html.Div(
            content,
            style={
                'background-image': f'url({img})',
                'background-size': 'cover',
                'background-blend-mode': 'darken',
                'background-color': 'rgba(0, 0, 0, 0.5)',
                'color': 'white',
                'padding': '10px',
                "border-radius": "5px",
            }
        )
    else:
        return html.Div(
            content,
            style={
                'background-color': bgcolor,
                'color': 'white',
                'padding': '10px',
                "border-radius": "5px",
                "opacity": "1",
            }
        )


@app.callback(
    Output('tree-graph', 'elements', allow_duplicate=True),
    [Input('tree-graph', 'tapNodeData')],
    [State('tree-graph', 'elements')],
    prevent_initial_callbacks=True
)
def add_nodes_on_click(nodeData, elements, ):
    global nodes, edges
    if not nodeData:
        return create_tree_elements(nodes, edges)
    for element in elements:
        node_id = element['data']['id']
        if node_id in nodes.keys():
            nodes[node_id] = (nodes[node_id][0], element['position']['x'], element['position']['y'])
    clicked_node_id = nodeData['id']
    if len(edges) == 0:
        mode_ids = [node_id for node_id in nodes.keys() if node_id!=clicked_node_id]
        for node_id in mode_ids:
            del nodes[node_id]
    nodes_new, edges_new = create_new_node(nodes, edges, clicked_node_id)
    nodes.update(nodes_new)
    edges.extend(edges_new)
    return create_tree_elements(nodes, edges)

def create_new_node(nodes, edges, node_id, n_new=N_NEW_NODE, length=LENGTH_EDGE, angle_max = ANGLE_NEW_NODE):
    x0, y0 = nodes[node_id][1], nodes[node_id][2]
    to_node_ids = {i[0] for i in edges}
    from_node_idmap = {i[1]:i[0] for i in edges}

    if node_id in to_node_ids:
        return nodes, edges
    elif node_id in from_node_idmap.keys():
        from_node_id = from_node_idmap[node_id]
        x_from, y_from = nodes[from_node_id][1], nodes[from_node_id][2]
        angle_center = np.arctan2(y0 - y_from, x0 - x_from)
        angles = angle_center + np.linspace(-angle_max, angle_max, n_new+2)[1:-1]
    else:
        angles = np.array([2 * np.pi * i / n_new for i in range(n_new)])

    node_info = nodes[node_id][0]
    cnt = 0
    length_tmp = calc_length(length, nodes, x0, y0, angles)
    nodes_new = {}
    edges_new = []
    for node_info_new, edge_label in zip(node_info.nodes, node_info.edges_name):
        if node_info_new.node_id in nodes.keys():
            continue
        x = x0 + length_tmp * np.cos(angles[cnt])
        y = y0 + length_tmp * np.sin(angles[cnt])
        cnt += 1
        nodes_new[node_info_new.node_id] = (node_info_new, x, y)
        edges_new.append((node_id, node_info_new.node_id, edge_label))
        if cnt == n_new:
            break
    return nodes_new, edges_new

def calc_length(length, nodes, x0, y0, thetas, delta_r=SIZE_NODE):
    xs = np.array([nodes[k][1] for k in nodes.keys()])
    ys = np.array([nodes[k][2] for k in nodes.keys()])
    lengths = np.arange(1, 3, 0.1)*length
    for length_tmp in lengths:
        xs_0 = x0 + length_tmp * np.cos(thetas)
        ys_0 = y0 + length_tmp * np.sin(thetas)
        r_min = length
        for x_0,y_0 in zip(xs,ys):
            rs = np.sqrt((x_0 - xs_0)**2 + (y_0 - ys_0)**2)
            r_min = min(r_min, np.min(rs))
        if r_min > delta_r:
            return length_tmp
    return lengths[-1]

@app.callback(
    Output('tree-graph', 'elements', allow_duplicate=True),
    [Input('submit-val', 'n_clicks')],
    prevent_initial_callbacks=True
)
def reset_page(n_clicks):
    global nodes, edges
    # ctx = dash.callback_context
    # # if not ctx.triggered and n_clicks > 0:
    nodes, edges = init_page()
    return create_tree_elements(nodes, edges)

# マウスオーバー（一旦保留）
# @app.callback(
#     Output('tree-graph', 'elements', allow_duplicate=True),
#     [Input('tree-graph', 'mouseoverNodeData')],
#     prevent_initial_callbacks=True
# )
# def add_nodes_on_hover(nodeData):
#     if len(edges) == 0:
#         return create_tree_elements(nodes, edges)
#     # global nodes, edges
#     if not nodeData:
#         return create_tree_elements(nodes, edges)
#     clicked_node_id = nodeData['id']
#     if clicked_node_id not in nodes.keys():
#         return create_tree_elements(nodes, edges)
#     nodes_dammy = {k:v for k,v in nodes.items()}
#     edges_dammy = [e for e in edges]
#     nodes_new, edges_new = create_new_node(nodes_dammy, edges_dammy, clicked_node_id, n_new=3)
#     for node_id in nodes_new.keys():
#         nodes_new[node_id][0].opacity = 0.5
#         nodes_dammy[node_id] = nodes_new[node_id]
#     edges_dammy.extend(edges_new)
#     return create_tree_elements(nodes_dammy, edges_dammy)


# ############################## app ####################################
# アプリ実行
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8080, debug=IS_DEBUG)