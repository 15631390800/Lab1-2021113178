import pytest
from main import build_directed_graph, generate_by_bridge_words, find_shortest
import coverage
cov = coverage.Coverage()

input_file = "input.txt"
with open(input_file, "r") as file:
        text = file.read()
graph = build_directed_graph(text)

#没有在图中的词
def test_generate_by_bridge_words1():
    assert generate_by_bridge_words(graph, 'you are people') == ['you', 'are', 'people']

#在图中的词没有桥接词
def test_generate_by_bridge_words1():
    assert generate_by_bridge_words(graph, 'you are new find') == ['you', 'are', 'new', 'find']

#有桥接词
def test_generate_by_bridge_words2():
    assert generate_by_bridge_words(graph, 'just to out, explore new civiliztions') in [['just', 'to', 'find', 'out', 'explore', 'strange', 'new', 'civiliztions'] , ['just', 'to', 'seek', 'out', 'explore', 'strange', 'new', 'civiliztions']]

# if __name__ == '__main__':
#     pytest.main()