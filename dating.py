import random

from enum import Enum
from typing import List, Dict, Any

from agents import Environment, Agent, Action

import colorama
from colorama import Fore, Style  # for colored output

colorama.init()  # initialize colorama


# Separate Enum for dating actions
class DatingActionType(Enum):
    OBSERVE = "observe"  # Keep the basic observe action
    SEND_MESSAGE = "send_message"
    REQUEST_DATE = "request_date"
    ACCEPT_DATE = "accept_date"
    REJECT = "reject"
    EXPRESS_INTEREST = "express_interest"


class PersonalityTrait(Enum):
    OPENNESS = "openness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"


class Interest(Enum):
    SPORTS = "sports"
    MUSIC = "music"
    TRAVEL = "travel"
    FOOD = "food"
    TECH = "tech"
    ART = "art"
    GAMING = "gaming"
    READING = "reading"


class DatingEnvironment(Environment):
    def __init__(self):
        self.current_time = 0
        self.relationships = {}  # agent_id -> agent_id
        self.messages = []
        self.dates = []

    def get_state(self) -> Dict[str, Any]:
        return {
            "time": self.current_time,
            "relationships": self.relationships,
            "messages": self.messages,
            "dates": self.dates,
        }

    def is_valid_action(self, agent: "Agent", action: Action) -> bool:
        if action.type == DatingActionType.REQUEST_DATE:
            target_id = action.params["target_id"]
            # Can't request date if either person is in relationship
            return (
                agent.id not in self.relationships
                and target_id not in self.relationships
            )
        return True

    def update(self, agents: List["Agent"]) -> None:
        self.current_time += 1


class DatingAgent(Agent):
    def __init__(self, agent_id: str, name: str):
        super().__init__(agent_id)
        self.name = name

        self.state = {
            "personality": {trait: random.random() for trait in PersonalityTrait},
            "interests": random.sample(list(Interest), k=random.randint(2, 5)),
            "relationship_status": "single",
            "emotional_state": 0.5,
            "relationship_satisfaction": 1.0,
        }

    def perceive(self, environment: Environment) -> Dict[str, Any]:
        env_state = environment.get_state()
        return {
            "time": env_state["time"],
            "messages": [m for m in env_state["messages"] if m["to"] == self.id],
            "relationships": env_state["relationships"],
        }

    def decide(self, observation: Dict[str, Any]) -> Action:
        if random.random() < 0.1:  # 10% chance to take action
            if self.state["relationship_status"] == "single":
                return self._try_dating_action()
            else:
                return self._relationship_action()
        return Action(DatingActionType.OBSERVE, {})

    def update_satisfaction(self, partner: "DatingAgent") -> float:
        # Random events and compatibility affect satisfaction
        compatibility = self.calculate_compatibility(partner)
        random_event = random.uniform(-0.1, 0.1)  # Daily random happiness fluctuation

        # Update satisfaction
        self.state["relationship_satisfaction"] = max(
            0,
            min(
                1.0,
                self.state["relationship_satisfaction"]
                + random_event
                + (compatibility - 0.5) * 0.1,
            ),
        )
        return self.state["relationship_satisfaction"]

    def _try_dating_action(self) -> Action:
        if random.random() < 0.5:
            return Action(
                DatingActionType.EXPRESS_INTEREST, {"message": f"Hi! I'm {self.name}"}
            )
        return Action(
            DatingActionType.REQUEST_DATE,
            {"target_id": "random"},  # will be resolved by simulation
        )

    def _relationship_action(self) -> Action:
        return Action(DatingActionType.SEND_MESSAGE, {"message": "How are you?"})

    def calculate_compatibility(self, other: "DatingAgent") -> float:
        # Calculate personality similarity
        pers_diff = sum(
            abs(self.state["personality"][trait] - other.state["personality"][trait])
            for trait in PersonalityTrait
        )

        # Calculate shared interests
        shared_interests = len(
            set(self.state["interests"]) & set(other.state["interests"])
        )

        # Combine scores (personality similarity and shared interests)
        return (1 - pers_diff / len(PersonalityTrait)) * 0.5 + (
            shared_interests / 5
        ) * 0.5


class DatingSimulation:
    def __init__(self, num_agents: int):
        self.names = [
            "Alex",
            "Blair",
            "Casey",
            "Drew",
            "Eden",
            "Frankie",
            "Gray",
            "Harper",
            "Indie",
            "Jules",
            "Kennedy",
            "London",
            "Morgan",
            "Nico",
            "Oak",
            "Paris",
            "Quinn",
            "Riley",
            "Sage",
            "Taylor",
            "Union",
            "Val",
            "Winter",
            "Xen",
        ]
        random.shuffle(self.names)

        self.agents = [
            DatingAgent(str(i), self.names[i % len(self.names)])
            for i in range(num_agents)
        ]
        self.environment = DatingEnvironment()
        self.stats = {
            "messages_sent": 0,
            "dates_arranged": 0,
            "relationships_formed": 0,
        }


    def step(self):
        # Collect all actions
        actions = []
        for agent in self.agents:
            action = agent.act(self.environment)
            if action.type != DatingActionType.OBSERVE:
                actions.append((agent, action))

        # Process actions
        for agent, action in actions:
            if not self.environment.is_valid_action(agent, action):
                continue

            if action.type == DatingActionType.EXPRESS_INTEREST:
                # Find random single agent
                single_agents = [
                    a
                    for a in self.agents
                    if a.id != agent.id and a.state["relationship_status"] == "single"
                ]
                if single_agents:
                    target = random.choice(single_agents)
                    compatibility = agent.calculate_compatibility(target)
                    self._print_interaction(agent, target, compatibility)
                    self.stats["messages_sent"] += 1

            elif action.type == DatingActionType.REQUEST_DATE:
                # Similar to EXPRESS_INTEREST but might lead to relationship
                single_agents = [
                    a
                    for a in self.agents
                    if a.id != agent.id and a.state["relationship_status"] == "single"
                ]
                if single_agents:
                    target = random.choice(single_agents)
                    compatibility = agent.calculate_compatibility(target)
                    if compatibility > 0.7:  # Good match!
                        self._create_relationship(agent, target)
                    self.stats["dates_arranged"] += 1

        self._check_relationships()
        self.environment.update(self.agents)

        print("\n" + "=" * 50)
        # self.print_daily_summary()

        # if self.environment.current_time % 3 == 0:  # Every 3 days
        #     self.print_relationship_network()

        # if self.environment.current_time % 7 == 0:  # Weekly
        #     print("\nDetailed Agent Status:")
        #     for agent in self.agents:
        #         self.print_agent_details(agent)

    def _create_relationship(self, agent1: DatingAgent, agent2: DatingAgent):
        self.environment.relationships[agent1.id] = agent2.id
        self.environment.relationships[agent2.id] = agent1.id
        agent1.state["relationship_status"] = "in_relationship"
        agent2.state["relationship_status"] = "in_relationship"
        self.stats["relationships_formed"] += 1
        print(
            f"{Fore.GREEN}♥ {agent1.name} and {agent2.name} are now in a relationship!{Style.RESET_ALL}"
        )

    def _check_relationships(self):
        breakups = []

        # Check each relationship
        for agent_id, partner_id in list(self.environment.relationships.items()):
            agent = next(a for a in self.agents if a.id == agent_id)
            partner = next(a for a in self.agents if a.id == partner_id)

            # Update satisfaction for both
            agent_satisfaction = agent.update_satisfaction(partner)
            partner_satisfaction = partner.update_satisfaction(agent)

            # Chance of breakup increases as satisfaction decreases
            average_satisfaction = (agent_satisfaction + partner_satisfaction) / 2
            breakup_chance = (
                1 - average_satisfaction
            ) * 0.1  # 10% chance at lowest satisfaction

            if random.random() < breakup_chance:
                breakups.append((agent, partner))

        # Process breakups
        for agent, partner in breakups:
            self._break_relationship(agent, partner)

    def _break_relationship(self, agent1: DatingAgent, agent2: DatingAgent):
        # Remove from relationships
        del self.environment.relationships[agent1.id]
        del self.environment.relationships[agent2.id]

        # Update agent states
        agent1.state["relationship_status"] = "single"
        agent2.state["relationship_status"] = "single"

        # Reset satisfaction
        agent1.state["relationship_satisfaction"] = 1.0
        agent2.state["relationship_satisfaction"] = 1.0

        print(
            f"{Fore.RED}💔 {agent1.name} and {agent2.name} have broken up!{Style.RESET_ALL}"
        )

    def _print_interaction(
        self, agent1: DatingAgent, agent2: DatingAgent, compatibility: float
    ):
        color = Fore.BLUE if compatibility > 0.5 else Fore.YELLOW
        print(
            f"{color}{agent1.name} expresses interest in {agent2.name} "
            f"(Compatibility: {compatibility:.2f}){Style.RESET_ALL}"
        )

    def print_stats(self):
        single_count = sum(
            1 for a in self.agents if a.state["relationship_status"] == "single"
        )
        relationship_count = len(self.environment.relationships) // 2

        print("\n" + "=" * 50)
        print(f"{Fore.CYAN}Simulation Stats:{Style.RESET_ALL}")
        print(f"Singles: {single_count}")
        print(f"Couples: {relationship_count}")
        print(f"Messages Sent: {self.stats['messages_sent']}")
        print(f"Dates Arranged: {self.stats['dates_arranged']}")
        print(f"Relationships Formed: {self.stats['relationships_formed']}")
        print("=" * 50 + "\n")

    def print_agent_details(self, agent: DatingAgent):
        status = agent.state["relationship_status"]
        color = Fore.GREEN if status == "in_relationship" else Fore.BLUE
        print(f"{color}{agent.name} {status}{Style.RESET_ALL}")

    def print_daily_summary(self):
        print(f"\n{Fore.CYAN}=== Daily Summary ==={Style.RESET_ALL}")
        singles = sum(
            1 for a in self.agents if a.state["relationship_status"] == "single"
        )
        couples = len(self.environment.relationships) // 2
        print(f"Active Singles: {singles}")
        print(f"Happy Couples: {couples}")
        print(f"Messages Today: {self.stats['messages_sent']}")

    def print_relationship_network(self):
        print(f"\n{Fore.YELLOW}Current Relationships:{Style.RESET_ALL}")
        for agent_id, partner_id in self.environment.relationships.items():
            agent = next(a for a in self.agents if a.id == agent_id)
            partner = next(a for a in self.agents if a.id == partner_id)
            if agent_id < partner_id:  # Print each couple only once
                compatibility = agent.calculate_compatibility(partner)
                print(
                    f"  ♥ {agent.name} + {partner.name} (Compatibility: {compatibility:.2f})"
                )


def main():
    sim = DatingSimulation(200)

    print(
        f"{Fore.CYAN}Starting Dating Simulation with {len(sim.agents)} agents{Style.RESET_ALL}"
    )
    print("Press Enter to advance a day, Ctrl+C to stop\n")

    try:
        day = 0
        while True:
            print(f"\n{Fore.YELLOW}Day {day}{Style.RESET_ALL}")
            sim.step()
            sim.print_stats()

            day += 1

            if day % 7 == 0:
                input("\nPress Enter for next day...")
    except KeyboardInterrupt:
        print("\nSimulation ended by user")
        sim.print_stats()


if __name__ == "__main__":
    main()
