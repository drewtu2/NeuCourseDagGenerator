import pydot
from pathlib import Path 
from typing import Self


class ClassNode:
    def __init__(self, subject: str, class_id: str, course_name: str = ""):
        self.subject = subject
        self.class_id = class_id
        self.course_name = course_name
        self.prerequisites = set()  # Set of ClassNode objects that are prerequisites
        self.corequisites = set()   # Set of ClassNode objects that are corequisites

    def add_prerequisite(self, class_node: Self):
        self.prerequisites.add(class_node)

    def add_corequisite(self, class_node: Self):
        self.corequisites.add(class_node)

    def set_course_name(self, name: str):
        self.course_name = name

    def __repr__(self):
        return self.full_name()

    def id(self):
        return f"{self.subject}{self.class_id}"
    
    def full_name(self):
        return f"{self.subject}{self.class_id}:{self.course_name}"


class DependencyGraph:
    def __init__(self):
        self.nodes = {}  # Dictionary to store nodes keyed by (subject, class_id)

    def add_class(self, subject: str, class_id: str) -> ClassNode:
        if (subject, class_id) not in self.nodes:
            self.nodes[(subject, class_id)] = ClassNode(subject, class_id)
        return self.nodes[(subject, class_id)]

    def add_prerequisite(self, subject: str, class_id: str, prereq_subject: str, prereq_class_id: str):
        class_node = self.add_class(subject, class_id)
        prereq_node = self.add_class(prereq_subject, prereq_class_id)
        class_node.add_prerequisite(prereq_node)

    def add_corequisite(self, subject: str, class_id: str, coreq_subject: str, coreq_class_id: str):
        class_node = self.add_class(subject, class_id)
        coreq_node = self.add_class(coreq_subject, coreq_class_id)
        class_node.add_corequisite(coreq_node)

    def get_node(self, subject: str, class_id: str) -> ClassNode:
        return self.nodes[(subject, class_id)]

    def __repr__(self):
        return f"DependencyGraph(nodes={list(self.nodes.values())})"
    
    def export_dot_file(self, dir_name: str, graph_name: str, subject: list[str] = []):
        graph = pydot.Dot("my_graph", graph_type="digraph", bgcolor="white", rankdir="RL")


        nodes_to_render = set()
        rendered_nodes = set()

        # Seed the nodes to render with the inlier set.
        for key_node in self.nodes:
            node = self.nodes[key_node]
            if subject and node.subject not in subject:
                continue
            nodes_to_render.add(node)

        # Search through all nodes in the inlier set.
        while nodes_to_render:
            node = nodes_to_render.pop()
            pydot_node = pydot.Node(node.id(), shape="box", label=node.full_name())
            graph.add_node(pydot_node)
            rendered_nodes.add(node)
            
            for pre_req in node.prerequisites:
                graph.add_edge(pydot.Edge(node.id(), pre_req.id(), color="blue"))
                if pre_req not in rendered_nodes:
                    nodes_to_render.add(pre_req)
            for co_req in node.corequisites:
                graph.add_edge(pydot.Edge(node.id(), co_req.id(), color="green"))
                if co_req not in rendered_nodes:
                    nodes_to_render.add(co_req)
        
        # Add a legend to the graph.
        graphlegend = pydot.Cluster(graph_name="legend", label="Legend", fontsize="15", color="red", style="filled", fillcolor="lightgrey", rankdir="TB")
        legend1 = pydot.Node("CoReq", style="filled", fillcolor="green", shape="Mrecord", rank="same"); graphlegend.add_node(legend1)
        legend2 = pydot.Node('PreReq', style="filled", fillcolor="blue", shape="Mrecord", rank="same"); graphlegend.add_node(legend2)
        graph.add_subgraph(graphlegend)
        graph.add_edge(pydot.Edge(legend1, legend2, style="invis"))

        # Write.
        output_dir = Path(dir_name)
        output_dir.mkdir(parents=True, exist_ok=True)

        graph.write_raw(output_dir.joinpath(f"{graph_name}_raw.dot").as_posix())
        graph.write_png(output_dir.joinpath(f"{graph_name}.png").as_posix())
