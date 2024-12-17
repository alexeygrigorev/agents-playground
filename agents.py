from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


class ActionType(Enum):
    """Defines the types of actions an agent can take"""

    INTERACT = "interact"
    COMMUNICATE = "communicate"
    OBSERVE = "observe"
    MODIFY = "modify"


@dataclass
class Action:
    """Represents an action taken by an agent"""

    type: ActionType
    params: Dict[str, Any]


class Environment(ABC):
    """Abstract base class for environments"""

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """Returns the current state of the environment"""
        pass

    @abstractmethod
    def update(self, agents: List["Agent"]) -> None:
        """Updates the environment based on agents' actions"""
        pass

    @abstractmethod
    def is_valid_action(self, agent: "Agent", action: Action) -> bool:
        """Checks if an action is valid in the current environment state"""
        pass


class Agent(ABC):
    """Abstract base class for agents"""

    def __init__(self, agent_id: str):
        self.id = agent_id
        self.memory: List[Dict[str, Any]] = []
        self.state: Dict[str, Any] = {}  # Flexible state representation

    @abstractmethod
    def perceive(self, environment: Environment) -> Dict[str, Any]:
        """Processes observations from the environment"""
        pass

    @abstractmethod
    def decide(self, observation: Dict[str, Any]) -> Action:
        """Decides on next action based on observations"""
        pass

    def act(self, environment: Environment) -> Action:
        """Main action loop for the agent"""
        observation = self.perceive(environment)
        action = self.decide(observation)
        self.memory.append({"observation": observation, "action": action})
        return action


class Simulation:
    """Manages the simulation of agents in the environment"""

    def __init__(self, environment: Environment, agents: List[Agent]):
        self.environment = environment
        self.agents = agents
        self.tick = 0

    def step(self) -> None:
        """Executes one step of the simulation"""
        actions = []
        for agent in self.agents:
            action = agent.act(self.environment)
            if self.environment.is_valid_action(agent, action):
                actions.append((agent, action))

        # Update environment with valid actions
        self.environment.update(self.agents)
        self.tick += 1
