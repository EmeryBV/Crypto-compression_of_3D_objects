#!/usr/bin/env python3

import heapq
import collections
import sys
import os

# Little hack to have binary stdin/stdout

CHUNK_SIZE = 1024
EOF = -1


### PREDICTORS ###

class MarkovPredictor(object):
    """ Can predict the « len_after » next characters, based on the « len_before » previous characters seen. """
    def __init__(self, len_before=1, len_after=1):
        self.len_before, self.len_after = len_before, len_after
        self.text_end = b''
        self.before = collections.defaultdict(lambda: collections.defaultdict(int))
        self.count = 0

    def feed(self, text):
        len_added = len(text)
        text = self.text_end[-self.len_before-self.len_after:] + text
        self.text_end = text
        self.count += len_added

        for i in range(len(text) - len_added - self.len_after, len(text) - self.len_after):
            if i < self.len_before:
                continue
            self.before[text[i-self.len_before:i]][text[i:i+self.len_after]] += 1

    def predict(self):
        if self.len_before > 0:
            text = self.text_end[-self.len_before:]
        else:
            text = b''
        return {k: v / self.count for k, v in self.before[text].items()}


class FixedPredictor(object):
    """ Prediction based on a fixed set of probabilities. """
    def __init__(self, freqs):
        self.freqs = freqs

    def feed(self, text):
        pass

    def predict(self):
        return self.freqs


class FullCharsetPredictor(FixedPredictor):
    """ The full set of possible characters need to be known, or it will impossible to code them. """
    def __init__(self):
        freqs = {bytes((i,)): 1 for i in range(256)}
        freqs[EOF] = 1 # special data to indicate the end of the stream
        super(FullCharsetPredictor, self).__init__(freqs)


class UnboundedPredictor(object):
    """ A homemade predictor, that don't predict fixed-length strings, but can predict long ones. """
    def __init__(self, exponent=2, min_len_before=1):
        assert exponent >= 1 and min_len_before >= 1
        self.text = b''
        self.exponent = exponent
        self.min_len_before = min_len_before

    def feed(self, text):
        self.text += text

    def predict(self):
        text = self.text
        predictions = collections.defaultdict(float)
        predictions_todo = collections.defaultdict(list)

        if not text:
            return {}

        # On cherche directement à avoir le dernier caractère qui correspond,
        # c'est plus rapide que de se promener dans tout le texte.
        i = -1
        while True:
            i = text.find(text[-1], i + 1, -1)
            if i == -1:
                break

            # On compte le nombre de caractères identiques avec la fin du texte actuel
            matching_before = 1
            while text[i-matching_before] == text[-matching_before-1] and i - matching_before >= 0:
                matching_before += 1
            if matching_before >= self.min_len_before:
                predictions_todo[bytes((text[i+1],))].append((i, matching_before))

        while predictions_todo:
            prediction, l = predictions_todo.popitem()

            score = sum(i[1]**self.exponent for i in l) / len(text)
            if len(l) < 2:
                continue

            appended_count = 0
            created_count = 0

            for i, matching_before in l:
                if i + len(prediction) >= len(text) - 1:
                    continue

                p = predictions_todo[text[i+1:i+len(prediction)+2]]
                if p:
                    appended_count += 1
                else:
                    created_count += 1
                p.append((i, matching_before))

            if appended_count != len(l) - 1 or created_count != 1:
                predictions[prediction] += score

        return predictions


class RUnboundedPredictor(UnboundedPredictor):
    """ The same as the UnboundedPredictor, but its predictions are based
        only on the « length » last characters seen. """
    def __init__(self, length=1000, *args, **kwargs):
        self.length = length
        super(RUnboundedPredictor, self).__init__(*args, **kwargs)

    def feed(self, text):
        self.text = (self.text + text)[-self.length:]


### HUFFMAN ###

class TreeNode(object):
    def __init__(self, weight, label=None, left=None, right=None):
        assert label is not None or left is not None or right is not None
        self.label = label
        self.weight = weight
        self.left, self.right = left, right

    def __lt__(self, other):
        if self.weight == other.weight:
            try:
                return self.label < other.label
            except TypeError:
                return repr(self.label) < repr(other.label)
        return self.weight < other.weight

    def __gt__(self,other):
        if self.weight == other.weight:
            try:
                return self.label > other.label
            except TypeError:
                return repr(self.label) > repr(other.label)
        return self.weight > other.weight

    def is_leaf(self):
        return self.left is None and self.right is None

    def __repr__(self):
        if self.is_leaf():
            return 'TreeNode(%s, %s)' % (self.weight, self.label)
        return 'TreeNode(%s, %s, %s, %s)' % (self.weight, self.label, self.left, self.right)

def make_huffman_dict(trees):
    trees.sort()
    heapq.heapify(trees)

    while len(trees) > 1:
        childR, childL = heapq.heappop(trees), heapq.heappop(trees)
        parent = TreeNode(childL.weight + childR.weight, left=childL, right=childR)
        heapq.heappush(trees, parent)

    def build_dict(d, tree, prefix):
        if tree.is_leaf():
            d[tree.label] = prefix
        else:
            build_dict(d, tree.left, prefix + '0')
            build_dict(d, tree.right, prefix + '1')

    d = {}
    build_dict(d, trees[0], '')
    return d


### ENGINE ###

def binstr_to_bytes(binary_string):
    """ To convert a string like 01001101010101 to a series of bytes """
    assert len(binary_string) % 8 == 0
    output_buffer = bytearray()
    for i in range(0, len(binary_string), 8):
        output_buffer.append(int(binary_string[i:i+8], 2))
    return output_buffer

def bytes_to_binstr(b):
    """ To convert a series of bytes to a string containing its binary form """
    return ''.join('{:08b}'.format(i) for i in b)

class Engine():
    def __init__(self):
        self.predictors = {
                FullCharsetPredictor() : 1e-8,
                MarkovPredictor(0): 1,
                MarkovPredictor(): 5,
                UnboundedPredictor(2.5): 12,
        }

    def _huffman_dict(self):
        self.predictions = collections.defaultdict(lambda: [0, []])
        for predictor in self.predictors:
            for prediction, weight in predictor.predict().items():
                self.predictions[prediction][0] += weight * self.predictors[predictor]
                self.predictions[prediction][1].append(predictor)
        return make_huffman_dict([TreeNode(v[0], k) for k, v in self.predictions.items()])

    def compress(self, stream_in, stream_out):
        buffer_in = stream_in.read(CHUNK_SIZE)
        buffer_out = ''

        while buffer_in:
            huffman_dict = self._huffman_dict()

            to_encode = None
            best_ratio = 0
            for n in self.predictions:
                if n != EOF and buffer_in.startswith(n):
                    ratio = len(n) / len(huffman_dict[n])
                    if ratio > best_ratio:
                        to_encode = n
                        best_ratio = ratio

            buffer_out += huffman_dict[to_encode]
            if len(buffer_out) % 8 == 0:
                stream_out.write(binstr_to_bytes(buffer_out))
                buffer_out = ''

            buffer_in = buffer_in[len(to_encode):]
            if len(buffer_in) < CHUNK_SIZE:
                buffer_in = buffer_in + stream_in.read(CHUNK_SIZE)

            for predictor in self.predictors:
                predictor.feed(to_encode)

            #sys.stderr.write("{} bits encodés en {} bits.\n".format(len(to_encode)*8, len(huffman_dict[to_encode])))

        eof_sequence = self._huffman_dict()[-1]
        buffer_out += eof_sequence
        buffer_out += '0' * (8 - len(buffer_out) % 8)
        stream_out.write(binstr_to_bytes(buffer_out))

    def decompress(self, stream_in, stream_out):
        buffer_in = bytes_to_binstr(stream_in.read(CHUNK_SIZE))

        while buffer_in:
            for decompressed, huffman in self._huffman_dict().items():
                if buffer_in.startswith(huffman):
                    if decompressed == EOF:
                        return

                    stream_out.write(decompressed)

                    buffer_in = buffer_in[len(huffman):]
                    if len(buffer_in) < CHUNK_SIZE:
                        buffer_in += bytes_to_binstr(stream_in.read(CHUNK_SIZE))

                    for predictor in self.predictors:
                        predictor.feed(decompressed)
                    break
