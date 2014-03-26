# -*- coding: utf-8 -*-
from collections import defaultdict


class Trans(object):
    """
    翻译模型

    IBM - model 1 EM算法模型

    source: 原语言
    target: 目标语言

    >>> model = Trans(['i laugh', 'laugh loudly'], ['我 笑', '大声地 笑'])
    >>> print round(model['i']['我'], 3) # before
    0.5
    >>> model.em(10)
    >>> print round(model['i']['我'], 3) # after
    0.998
    """
    def __init__(self, source, target, n=0):
        """
        source: 原语言
        target: 目标语言
        ttable: (e|f)
        """
        self.source = source
        self.target = target
        self.ttable = defaultdict(lambda: defaultdict(float))
        for (s, t) in self._read(self.source, self.target):
            for sw in s:
                for tw in t:
                    self.ttable[sw][tw] += 1
        self._normalize()

    def __getitem__(self, item):
        return self.ttable[item]

    def _read(self, source, target):
        """
        读取平行文本
        """
        sourcef = source if isinstance(source, list) else open(source, 'r')
        targetf = target if isinstance(target, list) else open(target, 'r')
        for (s, t) in zip(sourcef, targetf):
            yield ([None] + s.strip().split(), t.strip().split())

    def _normalize(self):
        """
        规格化
        """
        for (sw, t) in self.ttable.iteritems():
            Z = sum(t.values())
            for tw in t:
                t[tw] = t[tw] / Z

    def em(self, n=1):
        """
        EM 算法
        """
        for i in xrange(n):
            count = defaultdict(float)
            total = defaultdict(float)
            #E步
            for (s, t) in self._read(self.source, self.target):
                for sw in s:
                    for tw in t:
                        c = self.ttable[sw][tw]
                        count[(sw, tw)] += c
                        total[tw] += c
            #M步
            for ((sw, tw), val) in count.iteritems():
                self.ttable[sw][tw] = val / total[tw]
            self._normalize()
            # self.n += 1


class Lang(object):
    """
    语言模型

    上下文无关概率模型

    >>> lm = Lang(['我 笑', '大声地 笑'])

    >>> print round(lm['我'], 3)
    0.25
    """
    def __init__(self, target):
        """
        target: 目标语言
        """
        self.table = defaultdict(float)
        for t in self._read(target):
            for tw in t:
                self.table[tw] += 1
        self._normalize()

    def __getitem__(self, item):
        return self.table[item]

    def _read(self, target):
        """
        读取目标语言文本(若需分词, 已分词)
        """
        targetf = target if isinstance(target, list) else open(target, 'r')
        for t in targetf:
            yield t.strip().split()

    def _normalize(self):
        """
        规则化
        """
        Z = sum(self.table.values())
        for (tw, pval) in self.table.iteritems():
            self.table[tw] = pval / Z


class Decode(object):
    """
    解码

    全局搜索

    ttable: 词对齐概率表
    lm: 语言模型概率表
    source: 需要翻译字符串
    """
    def __init__(self, ttable, lm, source):
        self.ttable = ttable
        self.lm = lm
        self.source = source
        self.decode_training()

    def decode_training(self):
        target = None
        best_p = 0
        for (tw, pval) in self.decode_pair():
            if pval > best_p:
                best_p = pval
                target = tw
        print "%s -- %s : %f" % (self.source, target, round(best_p, 5))

    def decode_pair(self):
        t = self.ttable[self.source]
        for tw in t:
            yield (tw, t[tw] * self.lm[tw])


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    # m1 = Trans('data/en', 'data/fr', 10)
    # lm = Lang('data/fr')
    # Decode(m1, lm, 'THE')
