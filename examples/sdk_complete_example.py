"""
Complete example demonstrating the AIConexus SDK

This example shows how simple and powerful the SDK is:
- Define agents with expertise
- They automatically collaborate
- Tool calling works with any LLM model
"""

import asyncio
import logging
from typing import List

from aiconexus.sdk import (
    SDKAgent,
    ExpertiseArea,
    ConnectionInfo,
    Tool
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========== EXAMPLE 1: SIMPLE AGENT WITH DEFAULTS ==========

async def example_simple_agent():
    """
    Simplest possible way to create an agent
    Everything is handled automatically
    """
    
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple Agent with Defaults")
    print("="*70)
    
    # Create agent - that's it!
    agent = SDKAgent(
        name="simple-agent",
        expertise=[
            ExpertiseArea("general-qa", confidence=0.85)
        ],
        llm_model="gpt-4",  # Or any other model
    )
    
    # Execute
    result = await agent.execute(
        task="What is machine learning?"
    )
    
    print(f"\n📋 Answer:\n{result.answer}")
    print(f"\n✅ Success: {result.success}")
    print(f"⏱️  Time: {result.execution_time_ms:.0f}ms")


# ========== EXAMPLE 2: CUSTOM TOOLS ==========

async def example_custom_tools():
    """
    Agent with custom tools
    """
    
    print("\n" + "="*70)
    print("EXAMPLE 2: Agent with Custom Tools")
    print("="*70)
    
    # Define custom tools
    def calculate_sum(numbers: list) -> float:
        """Calculate sum of numbers"""
        return sum(numbers)
    
    def calculate_average(numbers: list) -> float:
        """Calculate average of numbers"""
        return sum(numbers) / len(numbers) if numbers else 0
    
    custom_tools = [
        Tool(
            name="calculate_sum",
            description="Calculate the sum of numbers",
            func=calculate_sum
        ),
        Tool(
            name="calculate_average",
            description="Calculate the average of numbers",
            func=calculate_average
        ),
    ]
    
    # Create agent with custom tools
    agent = SDKAgent(
        name="math-agent",
        expertise=[
            ExpertiseArea("mathematics", confidence=0.9),
            ExpertiseArea("statistics", confidence=0.85)
        ],
        custom_tools=custom_tools,
        llm_model="gpt-4"
    )
    
    # Execute
    result = await agent.execute(
        task="Calculate the average of [10, 20, 30, 40, 50]"
    )
    
    print(f"\n📋 Answer:\n{result.answer}")
    print(f"\n🔧 Tool calls made:")
    for call in result.tool_calls:
        print(f"  - {call.tool_name}({call.tool_args}) = {call.result}")


# ========== EXAMPLE 3: MULTI-AGENT COLLABORATION ==========

async def example_multi_agent_collaboration():
    """
    Multiple agents collaborating
    They automatically find and contact each other
    """
    
    print("\n" + "="*70)
    print("EXAMPLE 3: Multi-Agent Collaboration")
    print("="*70)
    
    # Create different agents with different expertise
    planner = SDKAgent(
        name="planner",
        expertise=[
            ExpertiseArea("planning", confidence=0.95),
            ExpertiseArea("task-decomposition", confidence=0.88)
        ],
        llm_model="gpt-4"
    )
    
    analyzer = SDKAgent(
        name="data-analyst",
        expertise=[
            ExpertiseArea("data-analysis", confidence=0.92),
            ExpertiseArea("statistics", confidence=0.85)
        ],
        llm_model="gpt-4"
    )
    
    optimizer = SDKAgent(
        name="optimizer",
        expertise=[
            ExpertiseArea("optimization", confidence=0.95),
            ExpertiseArea("constraints", confidence=0.88)
        ],
        llm_model="gpt-4"
    )
    
    # Register agents (in production, this would go to a registry)
    agents = [planner, analyzer, optimizer]
    
    # Planner executes - it will automatically:
    # 1. Detect it needs analysis
    # 2. Find the analyzer agent
    # 3. Contact it
    # 4. Integrate the response
    # 5. Then contact optimizer
    # 6. Synthesize everything
    
    result = await planner.execute(
        task="Plan and optimize a data processing pipeline with analysis"
    )
    
    print(f"\n📋 Answer:\n{result.answer}")
    print(f"\n🤝 Interactions:")
    for interaction in result.interactions:
        print(f"  - Contacted {interaction.get('to_agent', 'unknown')}")
        print(f"    Status: {interaction.get('status', 'unknown')}")
        print(f"    Time: {interaction.get('execution_time_ms', 0):.0f}ms")


# ========== EXAMPLE 4: FORCING SPECIFIC AGENTS ==========

async def example_delegation_rules():
    """
    Force delegation to specific agents for certain tasks
    """
    
    print("\n" + "="*70)
    print("EXAMPLE 4: Delegation Rules")
    print("="*70)
    
    agent = SDKAgent(
        name="general-agent",
        expertise=[
            ExpertiseArea("general", confidence=0.7)
        ],
        delegation_rules={
            "legal*": "legal-expert",      # Force to legal expert
            "*optimization*": "optimizer",  # Force to optimizer
            "*analysis*": "analyst"         # Force to analyst
        },
        llm_model="gpt-4"
    )
    
    result = await agent.execute(
        task="Analyze the legal implications and optimize the solution"
    )
    
    print(f"\n📋 Answer:\n{result.answer}")
    print(f"\n📋 Delegation rules applied for specific task types")


# ========== EXAMPLE 5: WORKING WITH DIFFERENT LLM MODELS ==========

async def example_different_models():
    """
    Show that SDK works with ANY model
    Including models without native tool support
    """
    
    print("\n" + "="*70)
    print("EXAMPLE 5: Different LLM Models")
    print("="*70)
    
    # Works with GPT-4
    gpt_agent = SDKAgent(
        name="gpt-agent",
        expertise=[ExpertiseArea("general", 0.8)],
        llm_model="gpt-4"  # Native tool support
    )
    
    # Works with Claude
    # claude_agent = SDKAgent(
    #     name="claude-agent",
    #     expertise=[ExpertiseArea("general", 0.8)],
    #     llm_model="claude-3-opus"  # Native tool support
    # )
    
    # Works with Llama (NO native tool support)
    # The SDK automatically adds synthetic tool calling!
    # llama_agent = SDKAgent(
    #     name="llama-agent",
    #     expertise=[ExpertiseArea("general", 0.8)],
    #     llm_model="llama-2"  # NO native tool support
    #     # SDK handles this automatically!
    # )
    
    # Works with local models
    # local_agent = SDKAgent(
    #     name="local-agent",
    #     expertise=[ExpertiseArea("general", 0.8)],
    #     llm_model="local-model"  # Any local model
    # )
    
    print("✅ SDK automatically handles:")
    print("  - Native tool calling for GPT-4, Claude")
    print("  - Synthetic tool calling for Llama, Mistral, local models")
    print("  - Unified API across all models")


# ========== EXAMPLE 6: EXPERT SYSTEM ==========

async def example_expert_system():
    """
    Complex multi-agent expert system
    """
    
    print("\n" + "="*70)
    print("EXAMPLE 6: Expert System")
    print("="*70)
    
    # Create specialized experts
    legal_expert = SDKAgent(
        name="legal-expert",
        expertise=[
            ExpertiseArea("legal", 0.98),
            ExpertiseArea("compliance", 0.95),
            ExpertiseArea("contracts", 0.94)
        ]
    )
    
    tech_expert = SDKAgent(
        name="tech-expert",
        expertise=[
            ExpertiseArea("software-engineering", 0.98),
            ExpertiseArea("architecture", 0.95),
            ExpertiseArea("scalability", 0.92)
        ]
    )
    
    business_expert = SDKAgent(
        name="business-expert",
        expertise=[
            ExpertiseArea("business-strategy", 0.95),
            ExpertiseArea("market-analysis", 0.92),
            ExpertiseArea("finance", 0.88)
        ]
    )
    
    # Coordinator orchestrates
    coordinator = SDKAgent(
        name="coordinator",
        expertise=[
            ExpertiseArea("orchestration", 0.95),
            ExpertiseArea("decision-making", 0.9)
        ],
        auto_delegation=True  # Automatically find experts
    )
    
    # Coordinator delegates to experts
    result = await coordinator.execute(
        task="""
        Design a new AI startup:
        1. What legal structures are needed?
        2. What tech architecture should we use?
        3. What's the business model?
        """,
        context={
            "budget": "$5M",
            "timeline": "6 months",
            "team_size": "10"
        }
    )
    
    print(f"\n📋 Coordination Result:\n{result.answer}")
    print(f"\n🤝 Agents contacted:")
    for interaction in result.interactions:
        print(f"  - {interaction.get('to_agent')}")


# ========== EXAMPLE 7: SDK FEATURES DEMO ==========

async def example_sdk_features():
    """
    Showcase key SDK features
    """
    
    print("\n" + "="*70)
    print("EXAMPLE 7: SDK Features")
    print("="*70)
    
    agent = SDKAgent(
        name="demo-agent",
        expertise=[
            ExpertiseArea("general", 0.8),
            ExpertiseArea("ai", 0.85)
        ],
        verbose=True  # Verbose logging
    )
    
    print("\n✅ SDK Features Demonstrated:")
    
    # Feature 1: Expertise summary
    print("\n1️⃣  Expertise Summary:")
    summary = agent.get_expertise_summary()
    print(f"   Agent: {summary['agent_name']}")
    print(f"   Expertise areas: {len(summary['expertise'])}")
    for e in summary['expertise']:
        print(f"     - {e['domain']}: {e['confidence']:.0%}")
    
    # Feature 2: Tools summary
    print("\n2️⃣  Available Tools:")
    tools = agent.get_tools_summary()
    for tool in tools:
        print(f"   - {tool['name']}: {tool['description']}")
    
    # Feature 3: Automatic LLM setup
    print("\n3️⃣  Automatic LLM Setup:")
    print(f"   Model: {agent.llm_model}")
    print(f"   Temperature: {agent.temperature}")
    
    # Feature 4: Auto-delegation
    print("\n4️⃣  Auto-Delegation Enabled:")
    print(f"   Can contact other agents: {agent.auto_delegation}")
    print(f"   Delegation rules: {agent.delegation_rules}")
    
    # Feature 5: Execution
    print("\n5️⃣  Execute Task:")
    result = await agent.execute(
        task="Explain what makes a good AI agent architecture"
    )
    print(f"   Success: {result.success}")
    print(f"   Execution time: {result.execution_time_ms:.0f}ms")
    print(f"   Reasoning steps: {len(result.reasoning_steps)}")
    print(f"   Tool calls: {len(result.tool_calls)}")


# ========== MAIN ==========

async def main():
    """Run all examples"""
    
    # Uncomment examples to run
    
    # await example_simple_agent()
    # await example_custom_tools()
    # await example_multi_agent_collaboration()
    # await example_delegation_rules()
    # await example_different_models()
    # await example_expert_system()
    await example_sdk_features()
    
    print("\n" + "="*70)
    print("✅ All examples completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
