import os
import warnings
import logging
import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    BigInteger,
    DateTime,
    Float,
    ARRAY,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import ARRAY
from sentence_transformers import SentenceTransformer


Base = declarative_base()
warnings.filterwarnings("ignore")
Base = declarative_base()

logging.getLogger("sqlalchemy").setLevel(logging.ERROR)


class AgentConversation(Base):
    __tablename__ = "full_benchmark_anthropic"
    id = Column(Integer, primary_key=True)
    run_id = Column(BigInteger, nullable=False)
    tool = Column(String)
    status = Column(String)
    attempt = Column(String)
    stdout = Column(String)
    stderr = Column(String)
    total_tokens = Column(Integer)
    prompt_tokens = Column(Integer)
    response_tokens = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer)
    embedding = Column(ARRAY(Float))  # Store embedding as a numpy array


class AgentMemory:
    def __init__(self):
        self.database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        self.engine = create_engine(self.database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        # Initialize sentence transformer for encoding
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

    def save_conversation_memory(
        self,
        user_id,
        run_id,
        previous_subtask_tool,
        previous_subtask_result,
        previous_subtask_attempt,
        previous_subtask_output,
        previous_subtask_errors,
        total_tokens,
        prompt_tokens,
        response_tokens,
    ):
        session = self.Session()
        try:
            memory_text = f"Run ID: {run_id}\nUser ID: {user_id}\nTool: {previous_subtask_tool}\nStatus: {previous_subtask_result}\nAttempt: {previous_subtask_attempt}\nStdout: {previous_subtask_output}\nStderr: {previous_subtask_errors}"
            embedding = self.encoder.encode(memory_text).tolist()

            conversation = AgentConversation(
                user_id=user_id,
                run_id=run_id,
                tool=str(previous_subtask_tool),
                status=str(previous_subtask_result),
                attempt=str(previous_subtask_attempt),
                stdout=str(previous_subtask_output),
                stderr=str(previous_subtask_errors),
                embedding=embedding,
                total_tokens=total_tokens,
                prompt_tokens=prompt_tokens,
                response_tokens=response_tokens,
            )
            session.add(conversation)
            session.commit()
        finally:
            session.close()

    def get_conversation_memory(self, run_id):
        session = self.Session()
        try:
            # Short-term memory (last 5 steps)
            short_term_conversations = (
                session.query(AgentConversation)
                .filter_by(run_id=run_id)
                .order_by(AgentConversation.created_at.desc())
                .limit(5)
                .all()
            )
            short_term_memories = []
            for conversation in reversed(short_term_conversations):
                short_term_memories.append(
                    {
                        "tool": conversation.tool,
                        "status": conversation.status,
                        "attempt": conversation.attempt,
                        "stdout": conversation.stdout,
                        "stderr": conversation.stderr,
                        "total_tokens": conversation.total_tokens,
                        "prompt_tokens": conversation.prompt_tokens,
                        "response_tokens": conversation.response_tokens,
                    }
                )

            # Combine short-term and long-term memories
            full_output_mems = "Short-term Memory (Last 5 steps)\n" + "-" * 100 + "\n"
            for idx, item in enumerate(short_term_memories):
                formatted_string = "\n".join(
                    [f"{key}: {value}" for key, value in item.items()]
                )
                full_output_mems += (
                    f"Step {idx + 1}\n{formatted_string}\n" + "-" * 100 + "\n"
                )

            return full_output_mems
        finally:
            session.close()
