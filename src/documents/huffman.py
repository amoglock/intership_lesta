import heapq
from collections import Counter
from collections import namedtuple


class Node(namedtuple("Node", ["left", "right"])):
    def walk(self, code, acc):
        self.left.walk(code, acc + "0")
        self.right.walk(code, acc + "1")

class Leaf(namedtuple("Leaf", ["char"])):
    def walk(self, code, acc):
        code[self.char] = acc or "0"

def huffman_encode(s):
    priority_queue = []
    for ch, freq in Counter(s).items():
        priority_queue.append((freq, len(priority_queue), Leaf(ch)))
    heapq.heapify(priority_queue)
    count = len(priority_queue)
    while len(priority_queue) > 1:
        freq1, _count1, left = heapq.heappop(priority_queue)
        freq2, _count2, right = heapq.heappop(priority_queue)
        heapq.heappush(priority_queue, (freq1 + freq2, count, Node(left, right))) 
        count += 1
    code = {}
    if priority_queue:
        [(_freq, _count, root)] = priority_queue
        root.walk(code, "")
    return code


async def run_encode(text: str):
    code = huffman_encode(text)
    encoded = "".join(code[ch] for ch in text)
    return {"huffman_code": encoded}

