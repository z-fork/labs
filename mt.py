#encoding=utf8
from collections import defaultdict


class Trans(object):
    """
    翻译模型

    IBM - model 1 EM算法模型

    e: 原语言
    f: 目标语言
    """
    def __init__(self, e, f):
        """
        e: 原语言
        f: 目标语言
        t: (e|f)
        """
        self.e = e
        self.f = f
        self.t = defaultdict(lambda: defaultdict(float))
        for (ei, fi) in self._read(self.e, self.f):
            for ew in ei:
                for fw in fi:
                    self.t[ew][fw] += 1
        self._normalize()
        self.n = 0

    def __getitem__(self, item):
        return self.t[item]

    def _read(self, e_path, f_path):
        """
        读取平行文本
        """
        e = e_path if hasattr(e_path, 'read') else open(e_path, 'r')
        f = f_path if hasattr(f_path, 'read') else open(f_path, 'r')
        for (ei, fi) in zip(e, f):
            yield ([None] + ei.strip().split(), fi.strip().split())

    def _normalize(self):
        """
        规格化
        """
        for (ew, fw_t) in self.t.iteritems():
            Z = sum(fw_t.values())
            for fw in fw_t:
                fw_t[fw] = fw_t[fw] / Z

    def em(self, n=1):
        """
        EM 算法
        """
        for i in xrange(n):
            count = defaultdict(float)
            total = defaultdict(float)
            #E步
            for (e, f) in self._read(self.e, self.f):
                for ew in e:
                    for fw in f:
                        c = self.t[ew][fw]
                        count[(ew, fw)] += c
                        total[fw] += c
            #M步
            for ((ew, fw), val) in count.iteritems():
                self.t[ew][fw] = val / total[fw]
            self._normalize()
            self.n += 1


class Lang(object):
    """
    语言模型

    上下文无关概率模型
    """
    def __init__(self, f):
        """
        f: 目标语言
        """
        self.f = f
        self.p = defaultdict(float)
        for fi in self._read(self.f):
            for fw in fi:
                self.p[fw] += 1
        self._normalize()

    def __getitem__(self, item):
        return self.p[item]

    def _read(self, f_path):
        """
        读取目标语言文本(若需分词, 已分词)
        """
        f = f_path if hasattr(f_path, 'read') else open(f_path, 'r')
        for fi in f:
            yield fi.strip().split()

    def _normalize(self):
        """
        规则化
        """
        Z = len(self.p)
        for (fw, val) in self.p.iteritems():
            self.p[fw] = val / Z


class Decode(object):
    """
    解码

    全局搜索

    t: 翻译模型对象
    l: 语言模型对象
    s: 需要翻译字符串
    """
    def __init__(self, t, l, s):
        self.t = t
        self.l = l
        self.s = s
        self._decode()

    def _decode(self):
        fw_t = self.t[self.s]
        print fw_t
        print len(fw_t)
        print '------'
        f = ''
        pr = 0
        for fw in fw_t:
            print fw_t[fw], "\t", self.l[fw], "\t", fw_t[fw] * self.l[fw], "\t", fw
            if fw_t[fw] * self.l[fw] > pr:
                pr = fw_t[fw] * self.l[fw]
                f = fw
        print self.s, '--', f

if __name__ == '__main__':
    t = Trans('data/e.small', 'data/f.small')
    t.em(10)
    l = Lang('data/f.small')
    Decode(t, l, 'LETTER')
