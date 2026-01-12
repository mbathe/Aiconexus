"""Example: Hello World Agent"""

import asyncio
from uuid import uuid4

from aiconexus.core.agent import Agent


class HelloWorldAgent(Agent):
    """A simple agent that greets users"""

    async def initialize(self) -> None:
        """Initialize the agent"""
        print(f"Initializing {self.name} ({self.agent_id})")

        # Register a capability
        self.register_capability(
            capability_id="greet",
            name="Greeter",
            description="Greets the user by name",
            input_schema={"type": "object", "properties": {"name": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"greeting": {"type": "string"}}},
            sla={"latency_ms": 10, "availability_percent": 99.9, "timeout_ms": 1000},
            pricing={
                "model_type": "per_call",
                "base_cost": "0",
                "unit": "call",
                "currency": "AIC",
            },
        )

    async def shutdown(self) -> None:
        """Shutdown the agent"""
        print(f"Shutting down {self.name}")

    async def execute_capability(self, capability_id: str, input_params):
        """Execute a capability"""
        if capability_id == "greet":
            name = input_params.get("name", "World")
            return {"greeting": f"Hello, {name}! 👋"}
        return {"error": "Unknown capability"}


async def main():
    """Run the example"""
    agent = HelloWorldAgent(name="Hello World Agent")
    await agent.initialize()

    # Simulate capability execution
    result = await agent.execute_capability("greet", {"name": "Alice"})
    print(f"Result: {result}")

    await agent.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
