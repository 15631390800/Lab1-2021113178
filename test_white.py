import pytest
import coverage
import networkx as nx

# 假设find_bridge_words函数已经在同一个文件中定义，或者已经从其他模块导入
from main import find_bridge_words, build_directed_graph, generate_by_bridge_words, find_shortest

input_file = "input.txt"
with open(input_file, "r") as file:
        text = file.read()
graph = build_directed_graph(text)


cov = coverage.Coverage()

def test_find_bridge_words():
    
    # 测试存在一个桥接词的情况
    assert find_bridge_words(graph, 'to', 'strange') == ['explore']
    
    # 测试存在多个桥接词的情况
    assert find_bridge_words(graph, 'to', 'out') == ['seek','find']
    
    # 测试word1不在图中的情况
    assert find_bridge_words(graph, 'x', 'to') == None
    
    # 测试word2不在图中的情况
    assert find_bridge_words(graph, 'to', 'y') == None
    
    # 测试word1和word2都不在图中的情况
    assert find_bridge_words(graph, 'x', 'y') == None
    
    # 测试没有直接路径的情况
    assert find_bridge_words(graph, 'out', 'explore') == []




if __name__ == '__main__':
    cov.start()
    pytest.main()
    cov.stop()
    cov.save()

