import dataclasses


@dataclasses.dataclass
class Configuration:
    input_file: str


configuration = Configuration(
    input_file="",
)
