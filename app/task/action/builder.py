import importlib
import inspect
import pkgutil

from app.task.action.base import Action
from app.task.action.customer.logistics_track import LogisticsAction
from app.task.action.inner.listener import ActionListen
from app.task.action.inner.responser import ActionResponse
from app.task.action.register import ActionRegistry
from app.task.action.runner import ActionRunner

# 方法：注册内置action
def register_inner_action(action_runner:ActionRunner):
    action_runner.actionRegistry.registerAction(ActionResponse())
    action_runner.actionRegistry.registerAction(ActionListen())

# 方法：注册自定义action，根据包，把包里面类扫描处理注册
def register_customer_action(action_runner:ActionRunner):
    # 通过包路径，导入过来
    package = importlib.import_module("app.task.action.customer")

    # 遍历包里面所有模块
    for _,module_name,is_pkg in pkgutil.iter_modules(
            package.__path__,
            prefix=f"{package.__name__}."):
        # 判断是否文件夹
        if is_pkg:
            continue
        # 加载每个模块
        module = importlib.import_module(module_name)

        # 遍历
        for _,obj in inspect.getmembers(module,inspect.isclass):

            if not issubclass(obj,Action) or obj is Action:
                continue
            # if obj.__module__ != module.__name__:
            #     continue
            #把action类注册
            action_runner.actionRegistry.registerAction(obj())

# 统一方法
def build_action_runner()->ActionRunner:
    action_runner = ActionRunner(ActionRegistry())
    register_customer_action(action_runner)
    register_inner_action(action_runner)
    return action_runner