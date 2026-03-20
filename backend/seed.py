"""Seed data script — creates initial admin user and built-in templates."""

import asyncio
import sys
sys.path.insert(0, ".")

from app.config import get_settings
from app.core.security import hash_password
from app.database import Base, engine, async_session
# Import ALL models so Base.metadata.create_all can resolve all FKs
from app.models.tenant import Tenant  # noqa: F401 — must be before user
from app.models.user import User, Department
from app.models.agent import AgentTemplate  # noqa: F401
from app.models.llm import LLMModel  # noqa: F401
from app.models.task import Task  # noqa: F401
from app.models.skill import Skill  # noqa: F401
from app.models.tool import Tool  # noqa: F401
from app.models.participant import Participant  # noqa: F401
from app.models.channel_config import ChannelConfig  # noqa: F401
from app.models.schedule import AgentSchedule  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401
from app.models.plaza import PlazaPost, PlazaComment  # noqa: F401
from app.models.activity_log import AgentActivityLog  # noqa: F401
from app.models.org import OrgDepartment, OrgMember, AgentRelationship, AgentAgentRelationship  # noqa: F401
from app.models.system_settings import SystemSetting  # noqa: F401
from app.models.invitation_code import InvitationCode  # noqa: F401


async def seed():
    """Create tables and seed initial data."""
    settings = get_settings()

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created")

    async with async_session() as db:
        # Note: No default admin user is seeded.
        # The first user to register via the UI becomes platform_admin automatically.
        from sqlalchemy import select, func

        # 1. Default company (tenant)
        existing_tenant = await db.execute(select(Tenant).where(Tenant.slug == "default"))
        if not existing_tenant.scalar_one_or_none():
            db.add(Tenant(name="Default", slug="default", im_provider="web_only"))
            print("✅ Default company created")

        # 2. Built-in templates
        templates = [
            {
                "name": "Research Assistant",
                "description": "Digital staff for information gathering, competitive analysis, and industry research.",
                "icon": "🔬",
                "category": "research",
                "soul_template": "## Identity\nYou are a professional research assistant skilled at gathering and analyzing information.\n\n## Personality\n- Rigorous and thorough\n- Data-driven\n- Objective\n\n## Boundaries\n- Always cite sources\n- Avoid subjective judgments",
                "is_builtin": True,
            },
            {
                "name": "Project Management Assistant",
                "description": "Tracks project progress, tasks, and follow-up reminders.",
                "icon": "📋",
                "category": "management",
                "soul_template": "## Identity\nYou are an efficient project management assistant.\n\n## Personality\n- Organized\n- Proactive on follow-ups\n- Deadline-aware\n\n## Boundaries\n- Do not change project plans without approval\n- Escalate major decisions",
                "is_builtin": True,
            },
            {
                "name": "Customer Support Assistant",
                "description": "Handles inquiries, FAQs, and ticket-style support.",
                "icon": "💬",
                "category": "support",
                "soul_template": "## Identity\nYou are a warm, professional customer support assistant.\n\n## Personality\n- Friendly and patient\n- Solution-oriented\n\n## Boundaries\n- Do not promise beyond your authority\n- Escalate sensitive issues to humans",
                "is_builtin": True,
            },
            {
                "name": "Data Analyst",
                "description": "Queries data, builds reports, and explains trends.",
                "icon": "📊",
                "category": "analytics",
                "soul_template": "## Identity\nYou are a data analysis expert.\n\n## Personality\n- Precise\n- Strong at visualization\n- Insightful\n\n## Boundaries\n- Data security first\n- Never leak raw sensitive data",
                "is_builtin": True,
            },
            {
                "name": "Content Assistant",
                "description": "Drafts copy, reviews content, and helps with social posts.",
                "icon": "✍️",
                "category": "content",
                "soul_template": "## Identity\nYou are a creative content assistant.\n\n## Personality\n- Creative\n- Strong writing\n- Marketing-aware\n\n## Boundaries\n- Match brand voice\n- Human approval before publishing",
                "is_builtin": True,
            },
        ]

        for tmpl in templates:
            existing = await db.execute(
                select(AgentTemplate).where(AgentTemplate.name == tmpl["name"])
            )
            if not existing.scalar_one_or_none():
                db.add(AgentTemplate(**tmpl))
                print(f"✅ Template created: {tmpl['icon']} {tmpl['name']}")

        # 3. Default department
        existing_dept = await db.execute(select(Department).where(Department.name == "Headquarters"))
        if not existing_dept.scalar_one_or_none():
            db.add(Department(name="Headquarters"))
            print("✅ Default department created: Headquarters")

        # 4. Demo agents for platform admin (if admin has zero agents)
        from app.models.agent import Agent
        admin_result = await db.execute(select(User).where(User.role == "platform_admin"))
        admin_user = admin_result.scalar_one_or_none()
        if admin_user:
            agent_count_result = await db.execute(
                select(func.count()).select_from(Agent).where(Agent.creator_id == admin_user.id)
            )
            agent_count = agent_count_result.scalar()
            if agent_count == 0:
                demo_agents = [
                    {
                        "name": "Morty",
                        "role_description": "Research Assistant — focused on information gathering, competitive analysis, and industry research.",
                        "status": "idle",
                        "heartbeat_enabled": True,
                    },
                    {
                        "name": "Meeseeks",
                        "role_description": "Task Executor — focuses on completing specific tasks assigned by the user efficiently.",
                        "status": "idle",
                        "heartbeat_enabled": True,
                    },
                ]
                for agent_data in demo_agents:
                    agent = Agent(
                        creator_id=admin_user.id,
                        tenant_id=admin_user.tenant_id,
                        **agent_data,
                    )
                    db.add(agent)
                    await db.flush()

                    # Initialize workspace directories
                    from pathlib import Path
                    ws_root = Path(settings.AGENT_DATA_DIR) / str(agent.id)
                    try:
                        for sub in ["workspace", "memory", "skills"]:
                            (ws_root / sub).mkdir(parents=True, exist_ok=True)
                        soul_path = ws_root / "soul.md"
                        if not soul_path.exists():
                            soul_path.write_text(f"# {agent.name}\n\n{agent.role_description}\n", encoding="utf-8")
                        mem_path = ws_root / "memory" / "memory.md"
                        if not mem_path.exists():
                            mem_path.write_text("# Memory\n\n_Record important information and knowledge here._\n", encoding="utf-8")
                    except OSError:
                        pass  # AGENT_DATA_DIR may not be writable
                    print(f"✅ Demo agent created: {agent.name}")

        await db.commit()

    print("\n🎉 Seed data complete!")


if __name__ == "__main__":
    asyncio.run(seed())
