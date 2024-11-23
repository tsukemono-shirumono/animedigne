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
        self.opacity = 1
        # self.bgcolor = "MediumVioletRed"
    def trans_view_title(self, title):
        # 空白を改行化
        title = title.replace(" ", "\n")
        # カッコを改行化
        title = title.replace("(", "\n(")
        title = title.replace(")", ")\n")
        title = title.replace("「", "\n「")
        title = title.replace("」", "」\n")
        title = title.replace("『", "\n『")
        title = title.replace("』", "』\n")
        title = title.replace("【", "\n【")
        title = title.replace("】", "】\n")
        title = title.replace("〔", "\n〔")
        title = title.replace("〕", "〕\n")
        title = title.replace("《", "\n《")
        title = title.replace("》", "》\n")
        title = title.replace("〈", "\n〈")
        title = title.replace("〉", "〉\n")
        title = title.replace("｛", "\n｛")
        title = title.replace("｝", "｝\n")
        title = title.replace("｟", "\n｟")
        title = title.replace("｠", "｠\n")
        title = title.replace("｢", "\n｢")
        title = title.replace("｣", "｣\n")

        # 一部の記号を改行化
        title = title.replace(":", ":\n")
        title = title.replace("：", "：\n")
        title = title.replace(";", ";\n")
        title = title.replace("；", "；\n")
        title = title.replace(",", ",\n")
        title = title.replace("、", "、\n")
        title = title.replace("。", "。\n")
        title = title.replace("．", "．\n")
        title = title.replace("!", "!\n")
        title = title.replace("！", "！\n")
        title = title.replace("?", "?\n")
        title = title.replace("？", "？\n")
        title = title.replace("・", "\n・\n")
        title = title.replace("／", "\n／\n")
        title = title.replace("＼", "\n＼\n")
        # 連続する改行を1つに
        title = re.sub(r'\n+', '\n', title)
        # 先頭と末尾の改行を削除
        title = title.strip("\n")
        return title
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
    def edges_name(self) -> list:
        return ["" for _ in self._nodes_to]
    @property
    def data(self) -> dict:
        if self._data is None:
            with open(self.path_node, 'r', encoding='utf-8') as f:
                self._data = json.load(f, object_pairs_hook=OrderedDict)
        return self._data
    @property
    def title(self) -> str:
        title = self.data["Subinfo"].replace(" ", "\n")
        return self.trans_view_title(title)
    @property
    def description(self) -> str:
        return re.sub(r'\[.*?\]', '', self.data["SubinfoDescription"])
    @property
    def bgcolor(self) -> str:
        kind = self.data.get("SubinfoKind", None)
        return {
            "cv": "#510060",
            "duration": "#790053",
            "genre": "#C6095D",
            "source": "#DAA520",  # Modified color for "source"
            "tag": "#FD7E21",
            "thema_song_artist": "#0F7926",
            "year": "DimGray",
        }.get(kind, "#0b3d7e")
class AnimeInfo(NodeInfo):
    def __init__(self, node_id):
        super().__init__()
        self.node_id = str(node_id)
        self.path_node_parent = Path("data/node_anime/")
        self.path_node = self.path_node_parent/f"{node_id}.json"
        self.path_edge_parent = Path("data/edge/")
        self.path_edge = self.path_edge_parent/f"{node_id}.json"
        self.path_edge_label_parent = Path("data/edge_label/")
        self.path_edge_label = self.path_edge_label_parent/f"{node_id}.json"
        self.bgcolor = "#0b3d7e"
    @property
    def nodes(self) -> list:
        with open(self.path_edge, 'r', encoding='utf-8') as f:
            dics = json.load(f, object_pairs_hook=OrderedDict)
        dics = [
            SubInfo(k, self.node_id, v)
            for k,v in dics.items()
        ]
        # タグとカテゴリの重複を避ける
        ret = []
        names = set()
        for info in dics:
            name = info.title
            if name in names:
                continue
            names.add(name)
            ret.append(info)
        return ret
    @property
    def edges_name(self) -> list:
        with open(self.path_edge_label, 'r', encoding='utf-8') as f:
            lst = json.load(f, object_pairs_hook=OrderedDict)
        return list(lst)
    @property
    def data(self) -> dict:
        if self._data is None:
            with open(self.path_node, 'r', encoding='utf-8') as f:
                self._data = json.load(f, object_pairs_hook=OrderedDict)
        return self._data
    @property
    def title(self) -> str:
        title = self.data["title"].replace(" ", "\n")
        return self.trans_view_title(title)
    @property
    def description(self) -> str:
        return re.sub(r'\[.*?\]', '', self.data["description"])
    @property
    def imageURL(self) -> str:
        ret = self.data.get("imageURL", None)
        if ret=="":
            return None
        return ret