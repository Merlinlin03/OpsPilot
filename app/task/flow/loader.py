from pathlib import Path
from typing import Dict, List

import yaml

from app.task.flow.models import FlowsList, FlowSlot, Flow
from app.task.flow.steps import FlowStep, CollectSlotStep


class FlowLoader:

    # 加载单个文件
    # path:Path yaml文件路径
    def load(self, path:Path)->FlowsList:
        with open(path,'r',encoding='utf-8') as f:
            data = yaml.safe_load(f)

        print(data)
        # data是yaml文件转换dict
        # 从data里面获取所有slots
        slots = self._load_slots(
              data.get('slots',{}))

        # 从data里面获取所有flows
        flows = self._load_flows(
                data.get('flows', {}),slots)
        # 返回数据
        return FlowsList(flows=flows, slots=slots)

    # 从data里面获取所有slots
    def _load_slots(self,slots_data:dict[str,dict])->Dict[str,FlowSlot]:
        # 封装数据
        slots = {}
        # 遍历字典  items()
        for s_name,s_data in slots_data.items():
            slots[s_name] = FlowSlot(**s_data,name=s_name)
        return slots

    # 从data里面获取所有flows
    def _load_flows(self,flows_data:dict[str,dict],
                         slots_data:Dict[str,FlowSlot])->List[Flow]:
        # 封装最终数据
        flows: List[Flow] = []

        for flow_id,flow_data in flows_data.items():
            # 从每个flow_data获取steps，把每个flow_data里面steps数据封装对象FlowStep
            steps: List[FlowStep] = [
                FlowStep.from_dict(step_data)
                for step_data in flow_data['steps']
            ]

            # 获取步骤列表每个步骤，找到步骤类型是collect类型
            flow_slots: List[FlowSlot] = []
            # 遍历
            for step in steps:
                if isinstance(step,CollectSlotStep):
                    # Dict[str,FlowSlot]
                    flow_slots.append(slots_data[step.slot_name])

            # 封装每个Flow对象
            flow = Flow(
                id=flow_id,
                name=flow_data['name'],
                description=flow_data['description'],
                steps=steps,
                slots=flow_slots
            )
            # 放到列表
            flows.append(flow)
        return flows

    # 加载多个yaml文件
    def load_many(self,paths:List[Path])->FlowsList:
        flows: List[Flow] = []
        slots: Dict[str, FlowSlot] = {}
        # 遍历路径列表得到每个路径
        for path in paths:
            # 调用加载单个文件方法
            flows_list:FlowsList = self.load(path)
            # 放到flows   [1,2,] [3] = [1,2,3]
            flows.extend(flows_list.flows)
            #slots
            slots.update(flows_list.slots)
        return FlowsList(flows=flows, slots=slots)

if __name__ == '__main__':
    base_url = Path(__file__).parents[3]
    user_flow_url = base_url / 'flow_config' / 'user_flows.yml'
    system_flow_url = base_url / 'flow_config' / 'system_flows.yml'

    loader = FlowLoader()
    data1 = loader.load(user_flow_url)
    print("=="*50)
    print(data1)