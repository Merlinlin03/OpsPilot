from typing import Any

from app.task.action.base import Action


# 注册中心
class ActionRegistry:
    def __init__(self) :
        self.actions:dict[str,Any] = {}

    # 注册
    def registerAction(self,action:Action):
        self.actions[action.name] = action

    # 根据action名称获取action对象
    def getAction(self,name:str)->Action:
        if name not in self.actions:
            raise Exception(f"Action {name} not registered")
        return self.actions[name]