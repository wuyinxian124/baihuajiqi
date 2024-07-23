# from modelscope.pipelines import pipeline
# word_segmentation = pipeline('word-segmentation',model='damo/nlp_structbert_word-segmentation_chinese-base')
#


import numpy as np
import scipy
print(scipy.__version__)


import gensim
print(gensim.__version__)

from gensim.models import KeyedVectors

# 加载预训练的 Google News Word2Vec 模型
model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)

# 获取单词的向量表示
vector = model['cat']
print(vector)


