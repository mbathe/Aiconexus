"""
Tests pour le système de types du SDK.
"""
import pytest
from datetime import datetime
import uuid

from src.aiconexus.sdk.types import (
    ExpertiseArea, ExpertiseLevel, AgentInfo, Message,
    AgentSchema, InputSchema, OutputSchema, FieldSchema,
    Tool, ToolCall, ReasoningStep, AgentResult
)


class TestExpertiseArea:
    """Tests pour ExpertiseArea."""
    
    def test_create_expertise_area(self):
        """Test la création d'une aire d'expertise."""
        expertise = ExpertiseArea(
            domain="data-analysis",
            level=ExpertiseLevel.EXPERT
        )
        
        assert expertise.domain == "data-analysis"
        assert expertise.level == ExpertiseLevel.EXPERT
    
    def test_expertise_all_levels(self):
        """Test tous les niveaux d'expertise."""
        levels = [
            ExpertiseLevel.NOVICE,
            ExpertiseLevel.INTERMEDIATE,
            ExpertiseLevel.EXPERT,
            ExpertiseLevel.MASTER
        ]
        
        for level in levels:
            expertise = ExpertiseArea(domain="test", level=level)
            assert expertise.level == level


class TestFieldSchema:
    """Tests pour FieldSchema."""
    
    def test_create_field_schema(self):
        """Test la création d'un schéma de champ."""
        schema = FieldSchema(
            type="string",
            description="Test field",
            constraints={"min_length": 1, "max_length": 100}
        )
        
        assert schema.type == "string"
        assert schema.description == "Test field"
        assert schema.constraints["min_length"] == 1
    
    @pytest.mark.parametrize("field_type", [
        "string", "number", "boolean", "array", "object"
    ])
    def test_all_field_types(self, field_type):
        """Test tous les types de champs."""
        schema = FieldSchema(type=field_type, description="Test")
        assert schema.type == field_type


class TestInputSchema:
    """Tests pour InputSchema."""
    
    def test_create_input_schema(self):
        """Test la création d'un schéma d'entrée."""
        fields = {
            "name": FieldSchema(type="string", description="User name"),
            "age": FieldSchema(type="number", description="User age")
        }
        
        schema = InputSchema(
            fields=fields,
            required_fields=["name"]
        )
        
        assert "name" in schema.fields
        assert "age" in schema.fields
        assert "name" in schema.required_fields
        assert "age" not in schema.required_fields
    
    def test_input_schema_all_required(self):
        """Test schéma avec tous les champs requis."""
        fields = {"a": FieldSchema(type="string"), "b": FieldSchema(type="number")}
        schema = InputSchema(fields=fields, required_fields=["a", "b"])
        
        assert len(schema.required_fields) == 2


class TestAgentInfo:
    """Tests pour AgentInfo."""
    
    def test_create_agent_info(self, data_analysis_expertise, simple_agent_schema):
        """Test la création d'une info d'agent."""
        agent = AgentInfo(
            id="agent-1",
            name="TestAgent",
            endpoint="http://localhost:8000",
            expertise=[data_analysis_expertise],
            schema=simple_agent_schema,
            status="active",
            created_at=datetime.now(),
            last_heartbeat=datetime.now()
        )
        
        assert agent.id == "agent-1"
        assert agent.name == "TestAgent"
        assert agent.status == "active"
        assert len(agent.expertise) == 1
    
    def test_agent_info_status_values(self, simple_agent_schema):
        """Test les valeurs de statut."""
        for status in ["active", "inactive", "degraded"]:
            agent = AgentInfo(
                id="test",
                name="test",
                endpoint="http://test",
                expertise=[],
                schema=simple_agent_schema,
                status=status,
                created_at=datetime.now(),
                last_heartbeat=datetime.now()
            )
            assert agent.status == status


class TestMessage:
    """Tests pour Message."""
    
    def test_create_message(self):
        """Test la création d'un message."""
        msg = Message(
            id="msg-1",
            sender_id="sender",
            recipient_id="recipient",
            data={"key": "value"},
            timestamp=datetime.now()
        )
        
        assert msg.id == "msg-1"
        assert msg.sender_id == "sender"
        assert msg.recipient_id == "recipient"
        assert msg.data["key"] == "value"
    
    def test_message_with_request_id(self):
        """Test un message avec request_id."""
        msg = Message(
            id="msg-1",
            sender_id="sender",
            recipient_id="recipient",
            data={},
            timestamp=datetime.now(),
            request_id="req-123"
        )
        
        assert msg.request_id == "req-123"
    
    def test_message_complex_data(self):
        """Test un message avec données complexes."""
        complex_data = {
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "number": 42,
            "bool": True
        }
        
        msg = Message(
            id="msg-1",
            sender_id="sender",
            recipient_id="recipient",
            data=complex_data,
            timestamp=datetime.now()
        )
        
        assert msg.data["list"] == [1, 2, 3]
        assert msg.data["dict"]["nested"] == "value"
        assert msg.data["number"] == 42
        assert msg.data["bool"] is True


class TestToolCall:
    """Tests pour ToolCall."""
    
    def test_create_tool_call(self):
        """Test la création d'un appel d'outil."""
        call = ToolCall(
            id="call-1",
            name="analyze",
            args={"data": [1, 2, 3]}
        )
        
        assert call.id == "call-1"
        assert call.name == "analyze"
        assert call.args["data"] == [1, 2, 3]


class TestReasoningStep:
    """Tests pour ReasoningStep."""
    
    def test_create_reasoning_step(self):
        """Test la création d'une étape de raisonnement."""
        step = ReasoningStep(
            iteration=0,
            thought="Let me analyze this",
            action_name="find_experts"
        )
        
        assert step.iteration == 0
        assert step.thought == "Let me analyze this"
        assert step.action_name == "find_experts"


class TestAgentResult:
    """Tests pour AgentResult."""
    
    def test_create_agent_result(self):
        """Test la création d'un résultat d'agent."""
        result = AgentResult(
            final_answer="The answer is 42",
            reasoning_steps=[],
            tool_calls=[],
            interactions=[],
            total_iterations=3,
            execution_time_ms=5000.5
        )
        
        assert result.final_answer == "The answer is 42"
        assert result.total_iterations == 3
        assert result.execution_time_ms == 5000.5
    
    def test_agent_result_with_steps(self):
        """Test un résultat avec étapes et appels d'outils."""
        steps = [
            ReasoningStep(iteration=0, thought="Step 1", action_name="tool1"),
            ReasoningStep(iteration=1, thought="Step 2", action_name="tool2")
        ]
        
        calls = [
            ToolCall(id="c1", name="tool1", args={}),
            ToolCall(id="c2", name="tool2", args={})
        ]
        
        result = AgentResult(
            final_answer="Done",
            reasoning_steps=steps,
            tool_calls=calls,
            interactions=[],
            total_iterations=2,
            execution_time_ms=1000.0
        )
        
        assert len(result.reasoning_steps) == 2
        assert len(result.tool_calls) == 2
        assert result.total_iterations == 2


class TestAgentSchema:
    """Tests pour AgentSchema."""
    
    def test_create_agent_schema(self, simple_input_schema, simple_output_schema):
        """Test la création d'un schéma d'agent."""
        schema = AgentSchema(
            name="TestAgent",
            input_schema=simple_input_schema,
            output_schema=simple_output_schema
        )
        
        assert schema.name == "TestAgent"
        assert schema.input_schema == simple_input_schema
        assert schema.output_schema == simple_output_schema
    
    def test_schema_consistency(self, simple_input_schema, simple_output_schema):
        """Test la cohérence du schéma."""
        schema = AgentSchema(
            name="Test",
            input_schema=simple_input_schema,
            output_schema=simple_output_schema
        )
        
        # Vérifier que les champs requis existent dans les champs
        for required in schema.input_schema.required_fields:
            assert required in schema.input_schema.fields


class TestToolClass:
    """Tests pour la classe Tool."""
    
    def test_tool_attributes(self):
        """Test les attributs d'un outil."""
        class TestTool(Tool):
            name = "test_tool"
            description = "A test tool"
            
            async def execute(self, **kwargs):
                return {"result": "success"}
        
        tool = TestTool()
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
    
    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test l'exécution d'un outil."""
        class AddTool(Tool):
            name = "add"
            description = "Add two numbers"
            
            async def execute(self, a: int, b: int):
                return {"result": a + b}
        
        tool = AddTool()
        result = await tool.execute(a=5, b=3)
        
        assert result["result"] == 8
