import json
from dataclasses import asdict
from typing import Any, Dict

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.domain.state import DialogueState
from app.infrastructure.llm import llm
from app.knowledge.intents import KNOWLEDGE_INTENTS
from app.plan.turn_plan import TurnPlan
from app.prompts.history_builder import HistoryBuilder
from app.prompts.loader import load_prompt
from app.task.flow.models import FlowsList


# 意图识别处理
class TurnPlanner:
    # 意图识别方法
    async def predict(self, state:DialogueState,
                      flows:FlowsList)->TurnPlan:
        # 1 构建提示词  todo
        input_prompt = self._build_input_prompt(state, flows)

        # 2 调用LLM得到结果
        turn_plan = await self._predict_promt_llm(input_prompt)

        # 3 把llm返回结果转换TurnPlan，返回
        return turn_plan

    # 构建提示词和调用llm过程
    async def _predict_promt_llm(self,
                                 input_prompt:Dict[str, Any])->TurnPlan:

        # 加载提示词 jinja2
        prompt_template_text = load_prompt("turn_plan")
        prompt_template = PromptTemplate.from_template(
                        template=prompt_template_text,
                        template_format="jinja2")

        chain = prompt_template | llm | JsonOutputParser()
        response:Dict[str,Any] = await chain.ainvoke(input_prompt)
        return TurnPlan.from_dict(response)

    # 找到提示词模型需要传递数据
    def _build_input_prompt(self,
                  state:DialogueState,flows_list:FlowsList)->Dict[str, Any]:
        # 1 user_message
        user_message = HistoryBuilder._render_user_message(
                            state.pending_turn.user_message)

        # 2 current_conversation
        ## 获取最近前十条历史
        current_conversation = HistoryBuilder.build(
               state.current_session().turns[-10:])

        # 3 focused_object_json
        # if state.focused_object is not None:
        #
        # else :

        focused_object_json = json.dumps(state.focused_object.to_dict()
                    if state.focused_object is not None  else None)

        # 4 active_task_json
        active_task_json = json.dumps(state.active_task.to_dict()
                       if state.active_task is not None else None)
        # 5 interrupted_tasks_json
        interrupted_tasks_json = json.dumps(
            [
                paused_task.to_dict()
                for paused_task in state.paused_tasks
            ],ensure_ascii=False
        )

        # 6 所有流程数据
        available_flows_json = json.dumps(
            # 把flows列表遍历，得到每个flow，去掉steps部分
            {"flows": [
                {
                  k: v  for k,v in asdict(flow).items() if k != "steps"}
                for flow in flows_list.flows]},ensure_ascii=False
        )

        return {
            "user_message": user_message,
            "current_conversation": current_conversation,
            "active_task_json": active_task_json,
            "interrupted_tasks_json": interrupted_tasks_json,
            "focused_object_json": focused_object_json,
            "available_flows_json": available_flows_json,
            "knowledge_intents_json": json.dumps(
                {
                    intent_id: {
                        "description": intent.description,
                        "requires_object": intent.requires_object,
                    }
                    for intent_id, intent in KNOWLEDGE_INTENTS.items()
                },
                ensure_ascii=False,
            )
        }
