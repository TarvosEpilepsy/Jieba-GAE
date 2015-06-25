# Jieba-GAE

为运行在gae而优化的jieba分词。

jieba分词：https://github.com/fxsjy/jieba

## 注意 ##
需要将未修改的jieba生成的缓存文件jieba.cache，并放置于tmp目录下。



## 用法 ##

均同时接受post和get请求

`/cut` 

	分词，接受参数：
    text：待分词内容
    cut_all：（可选）
        1: 全模式 .
        0: 精确模式

`/analyse` 

	关键词提取，接受参数：
    text：待分词内容
    mode：（可选）为TF-IDF时，则采用TF-IDF算法，否则基于TextRank 算法
	topK： 权重最大的关键词数量，默认值为 20
	withWeight：
	    1:返回权重
	    0:不返回权重
	allowPOS ：TF-IDF算法有效，仅包括指定词性的词。使用方法 ：allowPOS=n&allowPOS=nv&.......