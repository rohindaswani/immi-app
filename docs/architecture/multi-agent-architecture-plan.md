# Multi-Agent Architecture Implementation Plan

## Executive Summary

This document outlines the comprehensive plan to transform the Immigration Advisor application from a monolithic AI service into a sophisticated multi-agent system. This architecture will enable better scalability, fault tolerance, and specialized processing capabilities.

## Table of Contents

1. [Vision & Goals](#vision--goals)
2. [Current State Analysis](#current-state-analysis)
3. [Target Architecture](#target-architecture)
4. [Implementation Phases](#implementation-phases)
5. [Technical Specifications](#technical-specifications)
6. [Risk Management](#risk-management)
7. [Success Metrics](#success-metrics)

## Vision & Goals

### Primary Objectives
- **Scalability**: Handle 10,000+ concurrent users with sub-second response times
- **Specialization**: Deploy domain-specific AI models for optimal performance
- **Reliability**: Achieve 99.9% uptime with graceful degradation
- **Maintainability**: Reduce development cycle time by 40%
- **Cost Efficiency**: Optimize resource usage with selective scaling

### Business Value
- Reduce manual review time by 70%
- Improve user satisfaction scores to 4.5+/5.0
- Enable real-time compliance monitoring
- Support multi-language capabilities

## Current State Analysis

### Existing Architecture
```
┌─────────────────────────────────────┐
│         Frontend (React)            │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│      FastAPI Backend (Monolith)     │
│  ┌─────────────────────────────┐    │
│  │   ChatAIService (Single)    │    │
│  │  - Context gathering         │    │
│  │  - Rule-based responses     │    │
│  │  - LLM integration          │    │
│  └─────────────────────────────┘    │
└─────────────┬───────────────────────┘
              │
     ┌────────┴────────┬──────────┐
     ▼                 ▼          ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│PostgreSQL│  │ MongoDB  │  │  Redis   │
└──────────┘  └──────────┘  └──────────┘
```

### Pain Points
1. Single point of failure in AI service
2. Cannot scale specific functionalities independently
3. Long response times for complex queries
4. Difficult to add new capabilities without affecting existing code
5. Limited ability to use specialized models

## Target Architecture

### High-Level Design
```
┌─────────────────────────────────────┐
│         Frontend (React)            │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│      API Gateway (Kong/Envoy)       │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│    Agent Orchestration Layer        │
│        (LangGraph/Temporal)         │
└─────────────┬───────────────────────┘
              │
    ┌─────────┴──────────┬────────────┬────────────┬────────────┬──────────┐
    ▼                    ▼            ▼            ▼            ▼          ▼
┌──────────┐    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│Document  │    │Compliance│  │   Case   │  │Knowledge │  │   User   │  │Analytics │
│  Agent   │    │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │
└────┬─────┘    └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │               │              │              │              │              │
     └───────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    │         Event Bus (Kafka/RabbitMQ)      │
                    └────────────────────┬────────────────────┘
                                         │
                    ┌────────┬───────────┴───────────┬────────┐
                    ▼        ▼                       ▼        ▼
              ┌──────────┐ ┌──────────┐      ┌──────────┐ ┌──────────┐
              │PostgreSQL│ │ MongoDB  │      │  Redis   │ │Pinecone  │
              └──────────┘ └──────────┘      └──────────┘ └──────────┘
```

### Agent Specifications

#### 1. Document Intelligence Agent
**Purpose**: Automated document processing and information extraction

**Capabilities**:
- OCR with 99%+ accuracy for immigration documents
- Auto-classification of 20+ document types
- Entity extraction (dates, names, case numbers)
- Document validation and fraud detection

**Technology Stack**:
- **OCR**: Azure Form Recognizer / Tesseract
- **NLP**: spaCy, Transformers
- **ML**: Custom classification models
- **Storage**: MongoDB GridFS

**Resource Requirements**:
- 2 CPU cores, 4GB RAM (minimum)
- GPU optional for enhanced OCR

#### 2. Compliance Monitor Agent
**Purpose**: Proactive compliance tracking and alerting

**Capabilities**:
- Real-time status monitoring
- Deadline calculation and tracking
- Regulatory change detection
- Risk assessment scoring

**Technology Stack**:
- **Scheduler**: Temporal / Apache Airflow
- **Rules Engine**: Drools / Custom Python
- **Monitoring**: Prometheus metrics
- **Alerts**: SendGrid / Twilio

**Resource Requirements**:
- 1 CPU core, 2GB RAM
- High availability configuration

#### 3. Case Management Agent
**Purpose**: Handle complex multi-step immigration processes

**Capabilities**:
- Workflow orchestration
- Form auto-population
- Status tracking
- Dependency management

**Technology Stack**:
- **Workflow**: Temporal / Camunda
- **State Management**: XState
- **Forms**: React Hook Form
- **Storage**: PostgreSQL

**Resource Requirements**:
- 2 CPU cores, 4GB RAM
- Persistent storage for state

#### 4. Knowledge Base Agent
**Purpose**: Immigration law expertise and guidance

**Capabilities**:
- Semantic search across regulations
- Case law interpretation
- Policy change tracking
- Multi-language support

**Technology Stack**:
- **Vector DB**: Pinecone / Weaviate
- **LLM**: GPT-4, Claude
- **RAG**: LangChain
- **Search**: Elasticsearch

**Resource Requirements**:
- 2 CPU cores, 8GB RAM
- Vector storage capacity

#### 5. User Interaction Agent
**Purpose**: Natural language understanding and response generation

**Capabilities**:
- Context-aware conversations
- Intent classification
- Multi-turn dialogue
- Sentiment analysis

**Technology Stack**:
- **NLU**: Rasa / Dialogflow
- **LLM**: GPT-4 / Claude
- **Context**: Redis
- **Analytics**: Segment

**Resource Requirements**:
- 2 CPU cores, 4GB RAM
- Redis cache

#### 6. Analytics Agent
**Purpose**: Insights, predictions, and reporting

**Capabilities**:
- Processing time predictions
- Success rate analysis
- User behavior tracking
- Compliance risk scoring

**Technology Stack**:
- **Processing**: Apache Spark
- **ML**: scikit-learn, XGBoost
- **Time Series**: Prophet
- **Visualization**: Grafana

**Resource Requirements**:
- 4 CPU cores, 8GB RAM
- Time-series database

## Implementation Phases

### Phase 1: Foundation (Weeks 1-4)
**Goal**: Establish core infrastructure

**Tasks**:
- [ ] Set up message queue (Kafka/RabbitMQ)
- [ ] Deploy service mesh (Consul/Istio)
- [ ] Implement agent base framework
- [ ] Create event schema registry
- [ ] Set up monitoring infrastructure

**Deliverables**:
- Event bus operational
- Agent template and SDK
- Development environment
- CI/CD pipeline

**Code Structure**:
```python
# backend/app/agents/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
from app.core.events import EventBus

class BaseAgent(ABC):
    def __init__(self, agent_id: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.event_bus = EventBus()
        self.health_status = "healthy"

    @abstractmethod
    async def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message"""
        pass

    @abstractmethod
    async def validate_input(self, message: Dict[str, Any]) -> bool:
        """Validate input message"""
        pass

    async def publish_event(self, event_type: str, payload: Dict[str, Any]):
        """Publish event to event bus"""
        await self.event_bus.publish(event_type, payload)

    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            "agent_id": self.agent_id,
            "status": self.health_status,
            "capabilities": self.capabilities,
            "timestamp": datetime.utcnow().isoformat()
        }
```

### Phase 2: Core Agent Migration (Weeks 5-8)
**Goal**: Migrate existing ChatAIService to agent architecture

**Tasks**:
- [ ] Refactor ChatAIService into UserInteractionAgent
- [ ] Extract context gathering into separate service
- [ ] Implement agent communication protocols
- [ ] Create fallback mechanisms
- [ ] Migrate existing tests

**Deliverables**:
- UserInteractionAgent operational
- Context service decoupled
- Integration tests passing
- Performance benchmarks

**Migration Strategy**:
```python
# backend/app/agents/user_interaction.py
from app.agents.base import BaseAgent
from app.ai.context_service import ContextService
from app.core.events import EventTypes

class UserInteractionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="user-interaction-agent",
            capabilities=["chat", "context-aware-response", "intent-classification"]
        )
        self.context_service = ContextService()
        self.llm_client = self._initialize_llm()

    async def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        # Gather context
        context = await self._gather_context(message["user_id"])

        # Check if specialized agent needed
        intent = await self._classify_intent(message["content"])

        if intent == "document_query":
            # Delegate to Document Agent
            await self.publish_event(EventTypes.DOCUMENT_QUERY, {
                "user_id": message["user_id"],
                "query": message["content"],
                "context": context
            })
            return {"status": "delegated", "agent": "document-agent"}

        # Generate response
        response = await self._generate_response(message, context)

        # Publish response event
        await self.publish_event(EventTypes.RESPONSE_GENERATED, {
            "user_id": message["user_id"],
            "response": response
        })

        return response
```

### Phase 3: Specialized Agents (Weeks 9-12)
**Goal**: Deploy domain-specific agents

**Tasks**:
- [ ] Implement Document Intelligence Agent
- [ ] Deploy Compliance Monitor Agent
- [ ] Create Case Management Agent
- [ ] Set up Knowledge Base Agent
- [ ] Integrate Analytics Agent

**Deliverables**:
- All agents operational
- End-to-end workflows tested
- Performance metrics collected
- Documentation complete

**Agent Implementation Example**:
```python
# backend/app/agents/document_intelligence.py
class DocumentIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="document-intelligence-agent",
            capabilities=["ocr", "classification", "extraction", "validation"]
        )
        self.ocr_engine = self._initialize_ocr()
        self.classifier = self._load_classifier()
        self.extractor = self._initialize_extractor()

    async def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        document_path = message["document_path"]

        # Step 1: OCR
        text = await self.ocr_engine.extract_text(document_path)

        # Step 2: Classification
        doc_type = await self.classifier.classify(text)

        # Step 3: Entity Extraction
        entities = await self.extractor.extract_entities(text, doc_type)

        # Step 4: Validation
        is_valid = await self._validate_document(entities, doc_type)

        # Publish results
        await self.publish_event(EventTypes.DOCUMENT_PROCESSED, {
            "document_id": message["document_id"],
            "document_type": doc_type,
            "entities": entities,
            "is_valid": is_valid,
            "confidence": 0.95
        })

        # Trigger compliance check if needed
        if doc_type in ["i797", "i94", "visa"]:
            await self.publish_event(EventTypes.COMPLIANCE_CHECK_NEEDED, {
                "user_id": message["user_id"],
                "document_type": doc_type,
                "entities": entities
            })

        return {
            "status": "processed",
            "document_type": doc_type,
            "entities": entities,
            "is_valid": is_valid
        }
```

### Phase 4: Orchestration & Optimization (Weeks 13-16)
**Goal**: Implement complex workflows and optimize performance

**Tasks**:
- [ ] Implement workflow orchestration
- [ ] Create agent collaboration patterns
- [ ] Optimize inter-agent communication
- [ ] Implement caching strategies
- [ ] Performance tuning

**Deliverables**:
- Orchestration layer complete
- Complex workflows operational
- Performance targets met
- Load testing completed

**Orchestration Example**:
```python
# backend/app/orchestration/workflows.py
from langgraph import StateGraph, State
from app.agents import get_agent

class H1BRenewalWorkflow:
    def __init__(self):
        self.workflow = StateGraph(State)
        self._build_workflow()

    def _build_workflow(self):
        # Define nodes
        self.workflow.add_node("document_collection", self._collect_documents)
        self.workflow.add_node("compliance_check", self._check_compliance)
        self.workflow.add_node("form_preparation", self._prepare_forms)
        self.workflow.add_node("review", self._review_application)
        self.workflow.add_node("submission", self._submit_application)

        # Define edges
        self.workflow.add_edge("document_collection", "compliance_check")
        self.workflow.add_conditional_edge(
            "compliance_check",
            self._compliance_router,
            {
                "compliant": "form_preparation",
                "non_compliant": "document_collection"
            }
        )
        self.workflow.add_edge("form_preparation", "review")
        self.workflow.add_edge("review", "submission")

    async def _collect_documents(self, state: State) -> State:
        document_agent = get_agent("document-intelligence-agent")
        results = await document_agent.process({
            "action": "collect",
            "user_id": state["user_id"],
            "required_docs": state["required_documents"]
        })
        state["collected_documents"] = results["documents"]
        return state

    async def _check_compliance(self, state: State) -> State:
        compliance_agent = get_agent("compliance-monitor-agent")
        results = await compliance_agent.process({
            "action": "check",
            "user_id": state["user_id"],
            "documents": state["collected_documents"]
        })
        state["compliance_status"] = results["status"]
        state["compliance_issues"] = results.get("issues", [])
        return state
```

## Technical Specifications

### Infrastructure Requirements

#### Development Environment
```yaml
# docker-compose.yml
version: '3.8'
services:
  kafka:
    image: confluentinc/cp-kafka:latest
    ports:
      - "9092:9092"
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

  consul:
    image: consul:latest
    ports:
      - "8500:8500"
    command: agent -server -ui -bootstrap-expect=1 -client=0.0.0.0

  postgres:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: immigration_db
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    volumes:
      - postgres-data:/var/lib/postgresql/data

  mongodb:
    image: mongo:6
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db

volumes:
  redis-data:
  postgres-data:
  mongo-data:
```

#### Production Deployment (Kubernetes)
```yaml
# k8s/agents/document-agent-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: document-intelligence-agent
  namespace: immigration-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: document-agent
  template:
    metadata:
      labels:
        app: document-agent
    spec:
      containers:
      - name: agent
        image: immigration-app/document-agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: KAFKA_BROKERS
          value: "kafka-service:9092"
        - name: REDIS_HOST
          value: "redis-service"
        - name: MONGODB_URI
          valueFrom:
            secretKeyRef:
              name: mongodb-secret
              key: uri
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: document-agent-service
  namespace: immigration-app
spec:
  selector:
    app: document-agent
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: document-agent-hpa
  namespace: immigration-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: document-intelligence-agent
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Event Schema Registry
```python
# backend/app/core/events/schemas.py
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class EventTypes(Enum):
    # Document Events
    DOCUMENT_UPLOADED = "document.uploaded"
    DOCUMENT_PROCESSED = "document.processed"
    DOCUMENT_VALIDATED = "document.validated"

    # Compliance Events
    COMPLIANCE_CHECK_NEEDED = "compliance.check_needed"
    COMPLIANCE_ISSUE_DETECTED = "compliance.issue_detected"
    COMPLIANCE_CLEARED = "compliance.cleared"

    # User Events
    USER_QUERY = "user.query"
    RESPONSE_GENERATED = "user.response_generated"

    # Workflow Events
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"

class BaseEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventTypes
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_agent: str
    user_id: Optional[UUID] = None
    correlation_id: Optional[UUID] = None
    metadata: Dict[str, Any] = {}

class DocumentProcessedEvent(BaseEvent):
    event_type: EventTypes = EventTypes.DOCUMENT_PROCESSED
    document_id: UUID
    document_type: str
    entities: Dict[str, Any]
    confidence_score: float
    is_valid: bool
    processing_time_ms: int
```

### Monitoring & Observability
```python
# backend/app/core/monitoring.py
from prometheus_client import Counter, Histogram, Gauge
import logging
from opentelemetry import trace
from opentelemetry.exporter.jaeger import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Metrics
agent_requests = Counter(
    'agent_requests_total',
    'Total number of requests to agents',
    ['agent_id', 'operation', 'status']
)

agent_processing_time = Histogram(
    'agent_processing_duration_seconds',
    'Time spent processing requests',
    ['agent_id', 'operation']
)

agent_health_status = Gauge(
    'agent_health_status',
    'Health status of agents (1=healthy, 0=unhealthy)',
    ['agent_id']
)

# Tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

class AgentMonitoring:
    @staticmethod
    def track_request(agent_id: str, operation: str):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                with tracer.start_as_current_span(f"{agent_id}.{operation}") as span:
                    span.set_attribute("agent.id", agent_id)
                    span.set_attribute("operation", operation)

                    try:
                        with agent_processing_time.labels(agent_id, operation).time():
                            result = await func(*args, **kwargs)
                        agent_requests.labels(agent_id, operation, "success").inc()
                        return result
                    except Exception as e:
                        agent_requests.labels(agent_id, operation, "failure").inc()
                        span.set_attribute("error", True)
                        span.set_attribute("error.message", str(e))
                        raise
            return wrapper
        return decorator
```

## Risk Management

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Message queue failure | High | Medium | Implement queue redundancy, use persistent messages |
| Agent communication latency | Medium | Medium | Optimize serialization, implement caching |
| Data consistency issues | High | Low | Use event sourcing, implement saga pattern |
| Scaling bottlenecks | Medium | Medium | Horizontal scaling, load balancing |
| Model drift | Medium | Low | Continuous monitoring, A/B testing |

### Implementation Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Timeline delays | High | Medium | Phased rollout, parallel development tracks |
| Integration complexity | High | Medium | Comprehensive testing, gradual migration |
| Team skill gaps | Medium | Medium | Training sessions, pair programming |
| Legacy code conflicts | Medium | Low | Feature flags, backward compatibility |

### Mitigation Strategies

1. **Gradual Migration**
   - Use feature flags for controlled rollout
   - Maintain backward compatibility
   - Run old and new systems in parallel initially

2. **Comprehensive Testing**
   - Unit tests for each agent
   - Integration tests for workflows
   - Load testing for performance validation
   - Chaos engineering for resilience

3. **Monitoring & Alerting**
   - Real-time dashboards
   - Automated alerting
   - Performance tracking
   - Error rate monitoring

## Success Metrics

### Technical Metrics
- **Response Time**: < 500ms for 95th percentile
- **Throughput**: 1000+ requests/second
- **Availability**: 99.9% uptime
- **Error Rate**: < 0.1%
- **Agent Health**: 100% agents operational

### Business Metrics
- **User Satisfaction**: 4.5+ rating
- **Document Processing**: 95% automation rate
- **Compliance Accuracy**: 99%+ correct assessments
- **Cost Reduction**: 40% operational cost savings
- **Time to Resolution**: 70% reduction in case processing

### Development Metrics
- **Deployment Frequency**: Daily releases
- **Lead Time**: < 2 days from commit to production
- **MTTR**: < 30 minutes
- **Test Coverage**: > 80%
- **Code Quality**: A rating in SonarQube

## Rollout Strategy

### Stage 1: Alpha (Internal Testing)
- Deploy to development environment
- Internal team testing
- Performance benchmarking
- Bug fixes and optimization

### Stage 2: Beta (Limited Release)
- 10% of traffic routed to new system
- Monitor metrics closely
- Gather user feedback
- Iterate based on findings

### Stage 3: General Availability
- Gradual increase to 100% traffic
- Full monitoring in place
- Support team trained
- Documentation complete

### Stage 4: Optimization
- Performance tuning
- Cost optimization
- Feature enhancements
- Advanced analytics

## Maintenance & Support

### Documentation Requirements
- Agent API documentation
- Workflow diagrams
- Troubleshooting guides
- Performance tuning guide
- Disaster recovery procedures

### Training Plan
- Development team workshops
- Support team training
- User documentation
- Video tutorials

### Support Structure
- 24/7 on-call rotation
- Incident response procedures
- Escalation matrix
- Regular health checks

## Conclusion

This multi-agent architecture represents a significant evolution of the Immigration Advisor platform. By breaking down the monolithic AI service into specialized agents, we achieve:

1. **Better Performance**: Specialized agents with optimized models
2. **Higher Reliability**: Fault isolation and graceful degradation
3. **Easier Maintenance**: Clear separation of concerns
4. **Faster Development**: Independent agent development and deployment
5. **Cost Efficiency**: Scale only what needs scaling

The phased implementation approach ensures minimal disruption while gradually introducing the benefits of the new architecture. With proper monitoring, testing, and rollout strategy, this transformation will position the Immigration Advisor as a leading platform in immigration assistance technology.

## Appendices

### A. Technology Stack Summary
- **Languages**: Python 3.11+, TypeScript
- **Frameworks**: FastAPI, React, LangChain
- **Message Queue**: Apache Kafka / RabbitMQ
- **Databases**: PostgreSQL, MongoDB, Redis
- **Vector DB**: Pinecone / Weaviate
- **Orchestration**: LangGraph / Temporal
- **Monitoring**: Prometheus, Grafana, Jaeger
- **Deployment**: Kubernetes, Docker

### B. Estimated Costs (Monthly)
- **Development Environment**: $500
- **Staging Environment**: $1,500
- **Production Environment**: $5,000-10,000 (based on scale)
- **Third-party Services**: $2,000 (OCR, LLM APIs, etc.)

### C. Timeline Summary
- **Phase 1**: Weeks 1-4 (Foundation)
- **Phase 2**: Weeks 5-8 (Core Migration)
- **Phase 3**: Weeks 9-12 (Specialized Agents)
- **Phase 4**: Weeks 13-16 (Orchestration)
- **Total Duration**: 4 months

### D. Team Structure
- **Technical Lead**: 1
- **Backend Engineers**: 3
- **Frontend Engineers**: 2
- **DevOps Engineer**: 1
- **QA Engineer**: 1
- **Product Manager**: 1