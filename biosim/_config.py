import random
from pathlib import Path
from pprint import pprint
from typing import Literal, TypeAlias

import rtoml
from pydantic import (
    BaseModel,
    FieldValidationInfo,
    ValidationError,
    computed_field,
    field_validator,
)

ROOT = Path(__file__).parent

Trait: TypeAlias = Literal["", "智力", "体力", "外貌", "幸运"]


class WorldConfig(BaseModel):
    """地图相关配置"""

    width: int = 512  # 地图宽度
    height: int = 512  # 地图高度
    food_cost_rate: int = 2  # 食物消耗频率
    food_rate: float = 0.1  # 食物生成率
    food_refresh_rate: int = 10  # 食物刷新率


class CreatureConfig(BaseModel):
    """生物相关配置"""

    init_count: int = 100  # 初始生物数量


class GeneConfig(BaseModel):
    """基因相关配置"""

    init_gene_count: int = 100  # 初始基因数量
    coden_length: int = 3  # 密码子长度
    coden_table: list[Trait] = ["", "智力", "智力", "体力", "体力", "体力", "幸运", "外貌"]  # 密码子对应的性状
    mutation_rate: float = 1e-5  # 突变率

    @field_validator("coden_table", mode="after")
    def ensure_length(cls, v, values: FieldValidationInfo):
        coden_length = values.data["coden_length"]
        assert len(v) == 2**coden_length, f"coden_table长度[{len(v)}]不等于2^{coden_length}"
        return v

    @computed_field
    @property
    def base_num(self) -> int:
        """初始基因长度"""
        return self.init_gene_count * self.coden_length


class Config(BaseModel):
    """
    Class for holding configuration parameters for the BioSim simulation.
    """

    seed: int = 0  # 随机数种子
    world: WorldConfig = WorldConfig()
    gene: GeneConfig = GeneConfig()
    creature: CreatureConfig = CreatureConfig()

    def set_seed(self, seed: int = 0):
        self.seed = seed or self.seed
        if self.seed:
            random.seed(self.seed)

    @classmethod
    def load(cls, config_file: str = "user-config.toml"):
        """解析配置文件"""
        file = ROOT / config_file
        if not file.exists():
            return cls()
        with (ROOT / config_file).open(encoding="utf-8") as fp:
            user_config = rtoml.load(fp)
        return cls.model_validate(user_config)


try:
    config = Config.load()
    config.set_seed()
    pprint(config.model_dump(), indent=2, sort_dicts=False)
except ValidationError as e:
    print("配置文件错误：")
    pprint(e.errors())
    exit()
