from pathlib import Path
from collections import OrderedDict
import json
import re


class NodeInfo:
    def __init__(self):
        self.node_id = ""
        self.path_node = None
        self.path_node_parent = None
        self._data = None
        self.extra_info = ""
        self._data = None
        self.extra_info = ""
        self.bgcolor = "MediumVioletRed "
class SubInfo(NodeInfo):
    def __init__(self, node_id, node_id_from, nodes_to):
        super().__init__()
        self.node_id = f"{node_id}-{node_id_from}"
        self.path_node_parent = Path("data/node_subinfo/")
        self.path_node = self.path_node_parent/f"{node_id}.json"
        self._nodes_to = nodes_to
        self.imageURL = None
    @property
    def nodes(self) -> list:
        return [AnimeInfo(node_id) for node_id in self._nodes_to]
    @property
    def data(self) -> dict:
        if self._data is None:
            with open(self.path_node, 'r', encoding='utf-8') as f:
                self._data = json.load(f, object_pairs_hook=OrderedDict)
        return self._data
    @property
    def title(self) -> str:
        return self.data["Subinfo"].replace(" ", "\n")
    @property
    def description(self) -> str:
        return re.sub(r'\[.*?\]', '', self.data["SubinfoDescription"])
class AnimeInfo(NodeInfo):
    def __init__(self, node_id):
        super().__init__()
        self.node_id = str(node_id)
        self.path_node_parent = Path("data/node_anime/")
        self.path_node = self.path_node_parent/f"{node_id}.json"
        self.path_edge_parent = Path("data/edge/")
        self.path_edge = self.path_edge_parent/f"{node_id}.json"
        self.bgcolor = "#0b3d7e"
    @property
    def nodes(self) -> list:
        with open(self.path_edge, 'r', encoding='utf-8') as f:
            dics = json.load(f, object_pairs_hook=OrderedDict)
        dics = [
            SubInfo(k, self.node_id, v)
            for k,v in dics.items()
        ]
        return dics
    @property
    def data(self) -> dict:
        if self._data is None:
            with open(self.path_node, 'r', encoding='utf-8') as f:
                self._data = json.load(f, object_pairs_hook=OrderedDict)
        return self._data
    @property
    def title(self) -> str:
        return self.data["title"].replace(" ", "\n")
    @property
    def description(self) -> str:
        return re.sub(r'\[.*?\]', '', self.data["description"])
    @property
    def imageURL(self) -> str:
        ret = self.data.get("imageURL", None)
        if ret=="":
            return None
        return ret