import matplotlib.pyplot as plt
import tkinter as tk
import string
import random
import heapq
from collections import defaultdict, deque
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DirectedGraph:
    def __init__(self):
        self.graph = defaultdict(list)
        self.edge_weights = defaultdict(int)

    def add_edge(self, start, end):
        self.graph[start].append(end)
        self.edge_weights[(start, end)] += 1

    def neighbors(self, node):
        return self.graph[node]

    def nodes(self):
        return list(self.graph.keys())

    def edges(self):
        return [(start, end) for start in self.graph for end in self.graph[start]]

    def has_node(self, node):
        return node in self.graph

def preprocess_text(text):
    translation_table = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    cleaned_text = text.translate(translation_table)
    return cleaned_text.lower()

def traverse_graph(graph):
    node_names = []

    def dfs(node):
        node_names.append(node)
        for neighbor in graph.neighbors(node):
            if neighbor not in node_names:
                dfs(neighbor)

    for node in graph.nodes():
        if node not in node_names:
            dfs(node)
    return node_names

def build_directed_graph(text):
    cleaned_text = preprocess_text(text)
    words = cleaned_text.split()

    graph = DirectedGraph()

    for i in range(len(words) - 1):
        current_word = words[i]
        next_word = words[i + 1]
        if current_word != next_word:
            graph.add_edge(current_word, next_word)

    return graph

def draw_and_save_graph(graph, output_file):
    figure = plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(graph)

    nx.draw(graph, pos, with_labels=True, node_color='skyblue', node_size=500, edge_color='black', linewidths=1,
            arrowsize=20)

    edge_labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    plt.title("Directed Graph")
    plt.savefig(output_file)
    return figure

def all_simple_paths(graph, start, goal):
    def dfs(current, goal, path, visited, result):
        if current == goal:
            result.append(path[:])
            return
        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                path.append(neighbor)
                dfs(neighbor, goal, path, visited, result)
                path.pop()
                visited.remove(neighbor)

    result = []
    dfs(start, goal, [start], {start}, result)
    return result

def find_bridge_words(graph, word1, word2):
    if not graph.has_node(word1) or not graph.has_node(word2):
        return None

    try:
        all_paths = all_simple_paths(graph, word1, word2)
    except Exception:
        return None

    bridge_words = []

    for path in all_paths:
        if len(path) == 3:
            bridge_words.append(path[1])

    return bridge_words

def generate_by_bridge_words(graph, text):
    cleaned_text = preprocess_text(text)
    words = cleaned_text.split()
    word2add = []

    for i in range(len(words) - 1):
        bridge_words = find_bridge_words(graph, words[i], words[i + 1])
        if bridge_words:
            word2add.append((i, random.choice(bridge_words)))

    offset = 0
    for index, bridge_word in word2add:
        words.insert(index + 1 + offset, bridge_word)
        offset += 1

    return words

def all_shortest_paths(graph, start, target):
    queue = [(0, start, [])]
    min_dist = {start: 0}
    all_paths = []

    while queue:
        cost, current_node, path = heapq.heappop(queue)
        path = path + [current_node]

        if current_node == target:
            all_paths.append((cost, path))
            continue

        for neighbor in graph.neighbors(current_node):
            edge_weight = graph.edge_weights[(current_node, neighbor)]
            new_cost = cost + edge_weight

            if neighbor not in min_dist or new_cost <= min_dist[neighbor]:
                min_dist[neighbor] = new_cost
                heapq.heappush(queue, (new_cost, neighbor, path))

    if not all_paths:
        return None

    min_cost = min(all_paths, key=lambda x: x[0])[0]
    shortest_paths = [path for cost, path in all_paths if cost == min_cost]

    return shortest_paths

def find_shortest(graph, word1, word2):
    try:
        path = all_shortest_paths(graph, word1, word2)
        return path
    except Exception:
        return None

def random_walk(graph):
    current_node = random.choice(graph.nodes())
    visited_nodes = [current_node]
    visited_edges = []

    while True:
        if not graph.neighbors(current_node):
            break

        next_node = random.choice(graph.neighbors(current_node))
        visited_nodes.append(next_node)

        if (current_node, next_node) in visited_edges:
            break

        visited_edges.append((current_node, next_node))
        current_node = next_node

    return ' '.join(visited_nodes)

def show_graph_in_window(graph, output_file):
    figure = draw_and_save_graph(graph, output_file)

    window = tk.Toplevel()
    window.title("Graph")

    canvas = FigureCanvasTkAgg(figure, window)
    canvas.draw()
    canvas.get_tk_widget().pack()

def main():
    input_file = "input.txt"
    output_graph_file = "directed_graph.png"
    output_bridge_file = "bridge_words_output.txt"

    with open(input_file, "r") as file:
        text = file.read()

    def show_graph(graph, output_file, output_text):
        show_graph_in_window(graph, output_file)
        update_text_output(graph, output_text)

    def update_text_output(graph, output_text):
        output_text.tag_configure("header", font=("Helvetica", 12, "bold"), foreground="blue")
        output_text.tag_configure("content", font=("Helvetica", 10), foreground="black")
        output_text.delete("1.0", tk.END)

        output_text.insert(tk.END, "Nodes: ", "header")
        nodes_str = ', '.join(map(str, list(graph.nodes())))
        output_text.insert(tk.END, f"{nodes_str}\n", "content")

        output_text.insert(tk.END, "\nEdges: ", "header")
        edges_str = ', '.join(map(lambda edge: f"{edge[0]}->{edge[1]}", list(graph.edges())))
        output_text.insert(tk.END, f"{edges_str}\n", "content")

        output_text.insert(tk.END, "\n", "content")

    def open_graph_window():
        scrollable_window = tk.Toplevel(root)
        scrollable_window.title("有向图窗口")

        canvas = tk.Canvas(scrollable_window, width=800, height=600)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        bg_label = tk.Label(canvas, image=bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        output_frame_graph = tk.Frame(canvas)
        output_frame_graph.pack(pady=20)

        graph = build_directed_graph(text)
        button_draw_graph = tk.Button(output_frame_graph, text="有向图",
                                      command=lambda: show_graph(graph, output_graph_file, output_text_graph))
        button_draw_graph.pack(pady=20)

        output_text_graph = tk.Text(output_frame_graph, height=10, width=50)
        output_text_graph.pack(side=tk.LEFT, pady=20)

        scrollable_window.geometry("800x600")

    def open_shortpath_window():
        def show_shortest_path2(graph, word1, word2):
            shortest_path = find_shortest(graph, word1, word2)
            for i in range(len(shortest_path)):
                output_text2_short.insert(tk.END, f"Path {i + 1}: {' -> '.join(shortest_path[i])}\n", "content")

        short_path_window = tk.Toplevel(root)
        short_path_window.title("最短路径窗口")

        canvas = tk.Canvas(short_path_window, width=800, height=600)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        bg_label = tk.Label(canvas, image=bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        output_frame_short = tk.Frame(canvas)
        output_frame_short.pack(pady=20)

        label1_short = tk.Label(output_frame_short, text="单词1:")
        label1_short.pack()
        entry1_short = tk.Entry(output_frame_short)
        entry1_short.pack()

        label2_short = tk.Label(output_frame_short, text="单词2:")
        label2_short.pack()
        entry2_short = tk.Entry(output_frame_short)
        entry2_short.pack()

        graph = build_directed_graph(text)
        button_shortest_path = tk.Button(output_frame_short, text="显示最短路径",
                                         command=lambda: show_shortest_path2(graph, entry1_short.get(),
                                                                             entry2_short.get()))
        button_shortest_path.pack()

        output_text2_short = tk.Text(output_frame_short, height=10, width=50)
        output_text2_short.pack()

        output_text2_short.tag_configure("header", font=("Helvetica", 12, "bold"), foreground="blue")
        output_text2_short.tag_configure("content", font=("Helvetica", 10), foreground="black")
        short_path_window.geometry("800x600")

    def open_walk_window():
        random_walk_window = tk.Toplevel(root)
        random_walk_window.title("随机游走窗口")

        canvas = tk.Canvas(random_walk_window, width=800, height=600)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        bg_label = tk.Label(canvas, image=bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        output_frame_walk = tk.Frame(canvas)
        output_frame_walk.pack(pady=20)

        def show_random_walk2(graph):
            random_walk_result = random_walk(graph)
            output_text2_walk.insert(tk.END, random_walk_result, "content")

        graph = build_directed_graph(text)
        button_random_walk = tk.Button(output_frame_walk, text="随机游走", command=lambda: show_random_walk2(graph))
        button_random_walk.pack()

        output_text2_walk = tk.Text(output_frame_walk, height=10, width=50)
        output_text2_walk.pack()

        output_text2_walk.tag_configure("header", font=("Helvetica", 12, "bold"), foreground="blue")
        output_text2_walk.tag_configure("content", font=("Helvetica", 10), foreground="black")
        random_walk_window.geometry("800x600")

    def open_bridge_window():
        def show_bridge_words(graph, word1, word2):
            bridge_words = find_bridge_words(graph, word1, word2)
            if bridge_words is not None:
                bridge_words_str = ', '.join(bridge_words)
                output_text2_bridge.insert(tk.END, f"Bridge words: {bridge_words_str}\n", "content")
            else:
                output_text2_bridge.insert(tk.END, "No bridge words found\n", "content")

        bridge_window = tk.Toplevel(root)
        bridge_window.title("桥接词窗口")

        canvas = tk.Canvas(bridge_window, width=800, height=600)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        bg_label = tk.Label(canvas, image=bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        output_frame_bridge = tk.Frame(canvas)
        output_frame_bridge.pack(pady=20)

        label1_bridge = tk.Label(output_frame_bridge, text="单词1:")
        label1_bridge.pack()
        entry1_bridge = tk.Entry(output_frame_bridge)
        entry1_bridge.pack()

        label2_bridge = tk.Label(output_frame_bridge, text="单词2:")
        label2_bridge.pack()
        entry2_bridge = tk.Entry(output_frame_bridge)
        entry2_bridge.pack()

        graph = build_directed_graph(text)
        button_show_bridge = tk.Button(output_frame_bridge, text="显示桥接词",
                                       command=lambda: show_bridge_words(graph, entry1_bridge.get(), entry2_bridge.get()))
        button_show_bridge.pack()

        output_text2_bridge = tk.Text(output_frame_bridge, height=10, width=50)
        output_text2_bridge.pack()

        output_text2_bridge.tag_configure("header", font=("Helvetica", 12, "bold"), foreground="blue")
        output_text2_bridge.tag_configure("content", font=("Helvetica", 10), foreground="black")
        bridge_window.geometry("800x600")

    root = tk.Tk()
    root.title("程序主窗口")

    canvas = tk.Canvas(root, width=800, height=600)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    bg_image = tk.PhotoImage(file="3.png")
    bg_label = tk.Label(canvas, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    button1 = tk.Button(canvas, text="有向图窗口", command=open_graph_window)
    button1.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

    button2 = tk.Button(canvas, text="最短路径窗口", command=open_shortpath_window)
    button2.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

    button3 = tk.Button(canvas, text="随机游走窗口", command=open_walk_window)
    button3.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

    button4 = tk.Button(canvas, text="桥接词窗口", command=open_bridge_window)
    button4.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

    root.mainloop()

if __name__ == "__main__":
    main()
