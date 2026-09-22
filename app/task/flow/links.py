from dataclasses import dataclass

@dataclass(slots=True)
class FlowStepLink:
    target: str

# 无条件跳转
@dataclass(slots=True)
class StaticLink(FlowStepLink):
    pass

# 有条件跳转
@dataclass(slots=True)
class ConditionalLink(FlowStepLink):
    condition: str

# 条件不满足跳转
@dataclass(slots=True)
class FallbackLink(FlowStepLink):
    pass