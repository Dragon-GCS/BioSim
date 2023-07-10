from collections import defaultdict
import random
from functools import cache

from ._config import config

MASK = 2**config.gene.coden_length - 1  # 密码子掩码


class Genome:
    """基因组信息

    Attributes:
        _gene (int): 基因信息，用数字表示，每个bit位表示一个碱基，coden_length个碱基表示一个性状
        _base_num (int): 碱基数（比特数），可以通过竞争获取他人基因来增加碱基数
        _cached_traits (dict): 缓存的性状
    """

    __slots__ = "_gene", "_base_num"

    def __init__(self, gene: int = 0):
        self._base_num = config.gene.base_num
        if gene:
            self._gene = min(gene, 2**self._base_num - 1)
        else:
            self._gene = random.randint(1, 2**self._base_num - 1)

    def __str__(self) -> str:
        return f"{self._gene:0{self._base_num}b}"

    def __hash__(self) -> int:
        return self._gene

    def mutate(self) -> bool:
        """根据概率将随机一位碱基进行突变，并清空缓存的性状"""
        if random.random() > config.gene.mutation_rate:
            return False
        position = random.randint(0, self._base_num - 1)
        self._gene ^= 1 << position
        return True

    def recombine(self, other: "Genome") -> "Genome":
        """基因重组，将两个基因组以基因为单位进行随机重组"""
        position = random.randint(0, self._base_num - 1) // 3 * 3
        # 保留position左边的基因，右边的基因从other中获取
        new_gene = (self._gene >> position << position) | (other._gene & (2**position - 1))
        return Genome(new_gene)

    __and__ = recombine

    @property
    @cache
    def traits(self) -> defaultdict[str, int]:
        """根据基因获取性状, 并缓存。计算方法为基因不断右移，通过掩码获取密码子，再根据密码子表获取性状。

        例子:
            gene = 0b111101, coden_length = 3
            第一个性状为 gene >> 0 & MASK = 0b101 = 5，取密码子表索引为5的性状。
            第二个性状为 gene >> 3 & MASK = 0b111 = 7，取密码子表索引为7的性状。
        """
        traits = defaultdict(int)
        for i in range(0, self._base_num, config.gene.coden_length):
            trait = config.gene.coden_table[self._gene >> i & MASK]
            traits[trait] += 1
        return traits
