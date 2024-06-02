import matplotlib.pyplot as plt
import tkinter as tk
import networkx as nx
import string
import random
import heapq
from collections import defaultdict
from collections import deque
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk



def preprocess_text(text):
    # 替换非字母字符为空格
    translation_table = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    cleaned_text = text.translate(translation_table)
    return cleaned_text.lower()

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

def traverse_graph(graph):
    # 初始化一个空列表存储节点名称
    node_names = []

    # 定义一个辅助函数进行深度优先搜索
    def dfs(node):
        # 将当前节点加入到节点名称列表中
        node_names.append(node)

        # 遍历当前节点的所有邻居节点
        for neighbor in graph.neighbors(node):
            # 如果邻居节点还没有被访问过,递归访问它
            if neighbor not in node_names:
                dfs(neighbor)

    # 从图中任意一个节点开始进行深度优先搜索
    for node in graph.nodes():
        if node not in node_names:
            dfs(node)
    return node_names


def build_directed_graph(text):
    cleaned_text = preprocess_text(text)
    words = cleaned_text.split()

    # 创建有向图
    graph = nx.DiGraph()

    # 字典来存储每对相邻单词出现的次数
    edge_weights = defaultdict(int)

    # 遍历单词并记录权重
    for i in range(len(words) - 1):
        current_word = words[i].lower()
        next_word = words[i + 1].lower()
        if current_word != next_word:  # 排除自环
            edge_weights[(current_word, next_word)] += 1

    # 添加节点和边到图中
    for (current_word, next_word), weight in edge_weights.items():
        graph.add_edge(current_word, next_word, weight=weight)

    return graph


def draw_and_save_graph(graph, output_file):
    # 创建一个新的 Figure 对象
    figure = plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(graph)

    # 绘制节点和边
    nx.draw(graph, pos, with_labels=True, node_color='skyblue', node_size=500, edge_color='black', linewidths=1,
            arrowsize=20)

    # 获取边的权值
    edge_labels = nx.get_edge_attributes(graph, 'weight')

    # 绘制边的权值
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    plt.title("Directed Graph")

    # 保存图形到磁盘
    plt.savefig(output_file)
    return figure

def draw_and_save_graph_1(graph, paths, output_file):
    figure = plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(graph)

    # 绘制节点和边
    nx.draw(graph, pos, with_labels=True, node_color='skyblue', node_size=500, edge_color='black', linewidths=1,
            arrowsize=20)

    # 获取边的权值
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    # 高亮显示所有最短路径
    if paths:
        colors = plt.cm.get_cmap('tab10', len(paths))  # 使用颜色映射
        for idx, path in enumerate(paths):
            edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
            nx.draw_networkx_edges(graph, pos, edgelist=edges, edge_color=[colors(idx)], width=2.5)

    plt.title("Directed Graph with Shortest Paths")

    # 保存图形到磁盘
    plt.savefig(output_file)
    return figure


def all_simple_paths(graph, start, goal):
    def dfs(current, goal, path, visited, result):
        if current == goal:
            result.append(path[:])
            return
        for neighbor in graph[current]:
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
    if word1 not in graph or word2 not in graph:
        return None

    # 查找word1到word2的所有可能路径
    try:
        # all_paths = nx.all_simple_paths(graph, source=word1, target=word2)
        all_paths = all_simple_paths(graph, word1, word2)
    except nx.exception.NodeNotFound:
        return None

    # 初始化桥接词列表
    bridge_words = []

    # 遍历每条路径
    for path in all_paths:
        if len(path) == 3:  # 路径长度为3意味着有一个桥接词
            bridge_words.append(path[1])

    return bridge_words


def generate_by_bridge_words(graph, text):
    cleaned_text = preprocess_text(text)
    words = cleaned_text.split()
    word2add = []

    # 寻找所有可能的桥接词并记录
    for i in range(len(words) - 1):
        bridge_words = find_bridge_words(graph, words[i], words[i + 1])
        if bridge_words:
            word2add.append((i, random.choice(bridge_words)))

    # 按记录的位置插入桥接词
    offset = 0
    for index, bridge_word in word2add:
        words.insert(index + 1 + offset, bridge_word)
        offset += 1

    return words

def all_shortest_paths(graph, start, target, weight='weight'):
    # 使用优先队列跟踪当前节点的所有路径和距离
    queue = [(0, start, [])]  # (累计权重, 当前节点, 路径)
    min_dist = {start: 0}
    all_paths = []

    while queue:
        cost, current_node, path = heapq.heappop(queue)
        path = path + [current_node]

        if current_node == target:
            all_paths.append((cost, path))
            continue

        for neighbor, data in graph[current_node].items():
            edge_weight = data.get(weight, 1)
            new_cost = cost + edge_weight

            if neighbor not in min_dist or new_cost <= min_dist[neighbor]:
                min_dist[neighbor] = new_cost
                heapq.heappush(queue, (new_cost, neighbor, path))

    # 过滤出所有最短路径
    if not all_paths:
        return None

    min_cost = min(all_paths, key=lambda x: x[0])[0]
    shortest_paths = [path for cost, path in all_paths if cost == min_cost]

    return shortest_paths

def find_shortest(graph, word1, word2):
    try:
        # 使用Dijkstra算法查找带权图的最短路径
        path = all_shortest_paths(graph, word1, word2, weight='weight')
        figure = draw_and_save_graph_1(graph, path, "shortest_path.png")
        return path
    except nx.NetworkXNoPath:
        return None
    except nx.NodeNotFound:
        return None


def show_graph_in_window(graph, output_file):
    figure = draw_and_save_graph(graph, output_file)

    # 创建一个新的 Tkinter 顶层窗口
    window = tk.Toplevel()
    window.title("Graph")

    # 创建一个用于展示图形的 FigureCanvasTkAgg 对象
    canvas = FigureCanvasTkAgg(figure, window)
    canvas.draw()
    canvas.get_tk_widget().pack()


def main():
    input_file = "input.txt"  # 输入的文本文件路径
    output_graph_file = "directed_graph.png"  # 用于画图按钮的输出文件路径
    output_bridge_file = "bridge_words_output.txt"  # 用于桥连词按钮的输出文件路径

    with open(input_file, "r") as file:
        text = file.read()

    def show_graph(graph, output_file, output_text):
        show_graph_in_window(graph, output_file)

        # 更新画图按钮对应的文本框中的信息
        update_text_output(graph, output_text)

    def update_text_output(graph, output_text):
        # 定义Text组件中的不同标签样式
        output_text.tag_configure("header", font=("Helvetica", 12, "bold"), foreground="blue")
        output_text.tag_configure("content", font=("Helvetica", 10), foreground="black")

        # 清除Text组件的原有内容
        output_text.delete("1.0", tk.END)

        # 使用标签插入格式化后的文本
        output_text.insert(tk.END, "Nodes: ", "header")
        nodes_str = ', '.join(map(str, list(graph.nodes())))
        output_text.insert(tk.END, f"{nodes_str}\n", "content")

        output_text.insert(tk.END, "\nEdges: ", "header")
        edges_str = ', '.join(map(lambda edge: f"{edge[0]}->{edge[1]}", list(graph.edges())))
        output_text.insert(tk.END, f"{edges_str}\n", "content")

        # 可选：为每个段落添加空行以视觉上分隔
        output_text.insert(tk.END, "\n", "content")

    # ***************有向图*************
    def open_graph_window():
        # 创建一个新的 Toplevel 窗口
        scrollable_window = tk.Toplevel(root)
        scrollable_window.title("有向图窗口")

        # 创建一个 Canvas 组件,用于在其中显示内容
        canvas = tk.Canvas(scrollable_window, width=800, height=600)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建一个 label 并设置为背景
        bg_label = tk.Label(canvas, image=bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # 在 Canvas 组件中添加内容
        output_frame_graph = tk.Frame(canvas)
        output_frame_graph.pack(pady=20)

        # 相关的 UI 组件
        graph = build_directed_graph(text)
        button_draw_graph = tk.Button(output_frame_graph, text="有向图",
                                      command=lambda: show_graph(graph, output_graph_file, output_text_graph))
        button_draw_graph.pack(pady=20)

        output_text_graph = tk.Text(output_frame_graph, height=10, width=50)
        output_text_graph.pack(side=tk.LEFT, pady=20)

        # 设置 Toplevel 窗口的大小
        scrollable_window.geometry("800x600")

    # ***************最短路径*************
    def open_shortpath_window():
        def show_shortest_path2(graph, word1, word2):
            shortest_path = find_shortest(graph, word1, word2)
            for i in range(len(shortest_path)):
                output_text2_short.insert(tk.END,
                                        f"The shortest path from {word1} to {word2} is: {', '.join(shortest_path[i])}，len = {len(shortest_path[i])}\n")

        def show_shortest_paths(graph, word):
            node_names = traverse_graph(graph)
            node_names.remove(word)
            for node in node_names:
                show_shortest_path2(graph, word, node)

        def show_shortest_path(graph):
            word1 = input_entry3.get().lower()
            word2 = input_entry4.get().lower()
            if (word1 == ''):
                output_text2_short.delete("1.0", tk.END)  # 清空原有内容
                show_shortest_paths(graph, word2)
            elif (word2 == ''):
                output_text2_short.delete("1.0", tk.END)  # 清空原有内容
                show_shortest_paths(graph, word1)
            
            else:
                shortest_path = find_shortest(graph, word1, word2)
                output_text_short.delete("1.0", tk.END)  # 清空原有内容
                for i in range(len(shortest_path)):
                    output_text_short.insert(tk.END,
                                            f"The shortest path from {word1} to {word2} is: {', '.join(shortest_path[i])}，len = {len(shortest_path[i])}\n")

        # 创建一个新的 Toplevel 窗口
        scrollable_window = tk.Toplevel(root)
        scrollable_window.title("最短路径窗口")

        # 创建一个 Canvas 组件,用于在其中显示内容
        canvas = tk.Canvas(scrollable_window, width=800, height=600)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建一个 label 并设置为背景
        bg_label = tk.Label(canvas, image=bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # 在 Canvas 组件中添加内容
        output_frame_short_path = tk.Frame(canvas)
        output_frame_short_path.pack(pady=20)

        # 相关的 UI 组件
        input_label3 = tk.Label(output_frame_short_path, text="请输入第一个最短路径词：")
        input_label3.pack(side=tk.TOP, padx=10)
        input_entry3 = tk.Entry(output_frame_short_path)
        input_entry3.pack(side=tk.TOP)

        input_label4 = tk.Label(output_frame_short_path, text="请输入第二个最短路径词：")
        input_label4.pack(side=tk.TOP, padx=(10))
        input_entry4 = tk.Entry(output_frame_short_path)
        input_entry4.pack(side=tk.TOP)

        button_short_path = tk.Button(output_frame_short_path, text="展示最短路径",
                                      command=lambda: show_shortest_path(graph))
        button_short_path.pack(side=tk.TOP, pady=20)

        output_text_short = tk.Text(output_frame_short_path, height=5, width=50)
        output_text_short.pack()

        output_text2_short = tk.Text(output_frame_short_path, height=60, width=50)
        output_text2_short.pack()

        # 设置 Toplevel 窗口的大小
        scrollable_window.geometry("800x600")

    # ***************新文本生成*************
    def open_gentext_window():
        def gen_new_text(grapg):
            text1 = input_entry5.get().lower()
            text2 = generate_by_bridge_words(graph, text1)
            output_gen_text.delete("1.0", tk.END)  # 清空原有内容
            output_gen_text.insert(tk.END, f"The new sentence is: {' '.join(text2)}\n")
            # 创建一个新的 Toplevel 窗口

        scrollable_window = tk.Toplevel(root)
        scrollable_window.title("生成新文本窗口")

        # 创建一个 Canvas 组件,用于在其中显示内容
        canvas = tk.Canvas(scrollable_window, width=800, height=600)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建一个 label 并设置为背景
        bg_label = tk.Label(canvas, image=bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # 在 Canvas 组件中添加内容
        output_frame_gentext = tk.Frame(canvas)
        output_frame_gentext.pack(pady=20)

        # 相关的 UI 组件
        input_label5 = tk.Label(output_frame_gentext, text="请输入一段文本：")
        input_label5.pack(side=tk.TOP, padx=(10, 0))
        input_entry5 = tk.Entry(output_frame_gentext, width=40)
        input_entry5.pack(side=tk.TOP)

        button_gen_new_text = tk.Button(output_frame_gentext, text="生成新文本", command=lambda: gen_new_text(graph))
        button_gen_new_text.pack(side=tk.TOP, pady=20)

        output_gen_text = tk.Text(output_frame_gentext, height=5, width=50)
        output_gen_text.pack()

        # 设置 Toplevel 窗口的大小
        scrollable_window.geometry("800x600")

    # ***************桥接词*************
    def open_bridge_window():
        def find_bridge_words_button_click():
            word1 = input_entry1.get().lower()
            word2 = input_entry2.get().lower()
            if graph.has_node(word1) and graph.has_node(word2):
                bridge_words = find_bridge_words(graph, word1, word2)
                if bridge_words:
                    # 将桥连词输出到相应的文本框中
                    output_text_bridge.delete("1.0", tk.END)  # 清空原有内容
                    output_text_bridge.insert(tk.END,
                                              f"The bridge words from {word1} to {word2} are: {', '.join(bridge_words)}\n")
                else:
                    output_text_bridge.delete("1.0", tk.END)  # 清空原有内容
                    output_text_bridge.insert(tk.END, f"No bridge words from {word1} to {word2}!\n")
            else:
                output_text_bridge.delete("1.0", tk.END)  # 清空原有内容
                output_text_bridge.insert(tk.END, f"No {word1} or {word2} in the graph!\n")

        # 创建一个新的 Toplevel 窗口
        scrollable_window = tk.Toplevel(root)
        scrollable_window.title("桥接词窗口")

        # 创建一个 Canvas 组件,用于在其中显示内容
        canvas = tk.Canvas(scrollable_window, width=800, height=600)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建一个 label 并设置为背景
        bg_label = tk.Label(canvas, image=bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # 在 Canvas 组件中添加内容
        output_frame_bridge = tk.Frame(canvas)
        output_frame_bridge.pack(pady=20)

        # 最短路径相关的 UI 组件
        input_label1 = tk.Label(output_frame_bridge, text="请输入第一个桥接词：")
        input_label1.pack(side=tk.TOP, padx=10)
        input_entry1 = tk.Entry(output_frame_bridge)
        input_entry1.pack(side=tk.TOP)

        input_label2 = tk.Label(output_frame_bridge, text="请输入第二个桥接词：")
        input_label2.pack(side=tk.TOP, padx=(10, 0))
        input_entry2 = tk.Entry(output_frame_bridge)
        input_entry2.pack(side=tk.TOP)

        button_bridge_words = tk.Button(output_frame_bridge, text="桥接词", command=find_bridge_words_button_click)
        button_bridge_words.pack(side=tk.TOP, pady=20)

        output_text_bridge = tk.Text(output_frame_bridge, height=5, width=50)
        output_text_bridge.pack()

        # 设置 Toplevel 窗口的大小
        scrollable_window.geometry("800x600")

    # ***************随机游走**********************
    def open_randwalk_window():
        def random_walk(graph):
            # 随机选择起始节点
            current_node = random.choice(list(graph.nodes()))

            # 记录经过的节点和边
            visited_nodes = [current_node]
            visited_edges = []

            # 随机遍历直到出现重复边或没有出边的节点
            while True:
                # 如果当前节点没有出边，或者所有出边都已经访问过，停止遍历
                if not graph.out_edges(current_node):
                    break

                # 从当前节点的出边中随机选择一个
                next_node = random.choice(list(graph.successors(current_node)))

                # 记录经过的边和节点
                visited_nodes.append(next_node)

                if (current_node, next_node) in visited_edges:
                    break

                visited_edges.append((current_node, next_node))

                # 移动到下一个节点
                current_node = next_node

            sentence = ' '.join(visited_nodes)
            # 指定要保存的文件路径
            file_path = "random_walk.txt"

            # 将数据写入文本文件
            with open(file_path, "w") as file:
                file.write(sentence)

            output_randwalk.delete("1.0", tk.END)  # 清空原有内容
            output_randwalk.insert(tk.END, f"The random walk result is:\n {sentence}\n")
            output_randwalk.insert(tk.END, f"数据已成功写入文件: {file_path}\n")

        # 创建一个新的 Toplevel 窗口
        scrollable_window = tk.Toplevel(root)
        scrollable_window.title("随机游走窗口")

        # 创建一个 Canvas 组件,用于在其中显示内容
        canvas = tk.Canvas(scrollable_window, width=800, height=600)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建一个 label 并设置为背景
        bg_label = tk.Label(canvas, image=bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # 在 Canvas 组件中添加内容
        output_frame_randwalk = tk.Frame(canvas)
        output_frame_randwalk.pack(pady=20)

        # 相关的 UI 组件
        button_randwalk = tk.Button(output_frame_randwalk, text="开始随机游走", command=lambda: random_walk(graph))
        button_randwalk.pack(side=tk.TOP, pady=20)

        output_randwalk = tk.Text(output_frame_randwalk, height=5, width=50)
        output_randwalk.pack()

        # 设置 Toplevel 窗口的大小
        scrollable_window.geometry("800x600")

    # *********主窗口**********
    root = tk.Tk()
    root.title("GUI")
    root.geometry("600x600")  # 宽度 x 高度

    # 加载图片文件
    bg_image = tk.PhotoImage(file="3.png")

    # 创建一个 label 并设置为背景
    bg_label = tk.Label(root, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    label = tk.Label(root, text="软件工程实验一", font=("STLiti", 24, "bold"), fg="green")
    label.pack(pady=20)
    graph = build_directed_graph(text)
    # ************有向图************
    open_button = tk.Button(root, text="有向图", command=open_graph_window)
    open_button.pack(pady=15)

    # #************桥接词************
    open_button = tk.Button(root, text="桥接词", command=open_bridge_window)
    open_button.pack(pady=15)

    # ************生成新文本************
    open_button = tk.Button(root, text="生成新文本", command=open_gentext_window)
    open_button.pack(pady=15)

    # ************最短路径************
    open_button = tk.Button(root, text="最短路径", command=open_shortpath_window)
    open_button.pack(pady=15)

    # ************随机游走************
    open_button = tk.Button(root, text="随机游走", command=open_randwalk_window)
    open_button.pack(pady=15)

    root.mainloop()


if __name__ == "__main__":
    main()
