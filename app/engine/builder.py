from pathlib import Path

from app.chitchat.handler import ChitChatHandler
from app.clarify.responder import ClarifyResponder
from app.engine.dialogue_engine import DialogueEngine
from app.knowledge.handler import KnowLedgeHandler
from app.knowledge.intents import KNOWLEDGE_INTENTS
from app.knowledge.provider import (
    AdExperienceProvider,
    AppProfileProvider,
    FeedbackProvider,
    KnowledgeBaseProvider,
    SubscriptionProvider,
)
from app.knowledge.registry import KnowledgeProviderRegistry
from app.knowledge.responder import KnowledgeResponder
from app.plan.turn_planner import TurnPlanner
from app.plan.validator import TurnPlanValidator
from app.task.action.builder import build_action_runner
from app.task.action.register import ActionRegistry
from app.task.action.runner import ActionRunner
from app.task.command.process import CommandProcessor
from app.task.flow.executor import FlowExecutor
from app.task.flow.loader import FlowLoader
from app.task.handler import TaskHandler

# 获取yaml文件路径
PROJECT_DIR = Path(__file__).resolve().parents[2]
FLOW_FILE_DIR = PROJECT_DIR / 'flow_config'
FLOW_YAML_FILE = ["user_flows.yml","system_flows.yml"]

def build_dialogue_engine():
    flow_list = FlowLoader().load_many([FLOW_FILE_DIR / file_name
        for file_name in FLOW_YAML_FILE
    ])

    knowledge_registry = KnowledgeProviderRegistry([
        AppProfileProvider(),
        SubscriptionProvider(),
        FeedbackProvider(),
        AdExperienceProvider(),
        KnowledgeBaseProvider(),
    ])

    return DialogueEngine(
        turn_planner=TurnPlanner(),
        turn_plan_validator=TurnPlanValidator(),
        clarify_responder=ClarifyResponder(),
        chitchat_handler=ChitChatHandler(),
        knowledge_handler=KnowLedgeHandler(
            knowledge_intents=KNOWLEDGE_INTENTS,
            provider_registry=knowledge_registry,
            knowledge_responder=KnowledgeResponder(),
        ),
        task_handler=TaskHandler(
            flow_list=flow_list,
            processor=CommandProcessor(),
            flow_executor=FlowExecutor(),
            action_runner=build_action_runner(),
        ),
    )
