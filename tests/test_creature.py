from unittest import TestCase

from biosim import config, Genome


class TestGenome(TestCase):
    def setUp(self) -> None:
        self.gene = Genome()
        # 设置随机种子，调整突变概率为100%
        config.set_seed(1)
        config.gene.mutation_rate = 1.0
        config.gene.init_gene_count = 8

    def test_mutate(self):
        prev_gene = self.gene._gene
        # 突变后基因不相等，长度不变，缓存的性状被清空
        traits = self.gene.traits
        self.assertTrue(self.gene.mutate())
        self.assertNotEqual(prev_gene, self.gene._gene)
        self.assertEqual(len(str(self.gene)), self.gene._base_num)
        self.assertNotEqual(traits, self.gene.traits)
        print(traits, self.gene.traits)

    def test_recombine(self):
        genome_a = Genome()  # 001000100110010110110010
        genome_b = Genome()  # 100100011011011101011001
        new_genome = genome_a.recombine(genome_b)
        self.assertEqual(str(new_genome), "001000100110010110110010")
