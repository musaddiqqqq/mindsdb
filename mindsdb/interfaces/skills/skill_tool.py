from mindsdb.interfaces.storage import db
from mindsdb.integrations.handlers.langchain_handler.mindsdb_database_agent import MindsDBSQL

from typing import List


def _make_text_to_sql_tools(skill: db.Skills, llm, executor) -> List:
    # To prevent dependency on Langchain unless an actual tool uses it.
    try:
        from langchain.agents.agent_toolkits import SQLDatabaseToolkit
    except ImportError:
        raise ImportError('To use the text-to-SQL skill, please install langchain with `pip install langchain`')
    database = skill.params['database']
    tables = skill.params['tables']
    tables_to_include = [f'{database}.{table}' for table in tables]
    db = MindsDBSQL(
        engine=executor,
        metadata=executor.session.integration_controller,
        include_tables=tables_to_include
    )
    return SQLDatabaseToolkit(db=db, llm=llm).get_tools()


def make_tools_from_skill(skill: db.Skills, llm, executor) -> List:
    """Makes Langchain compatible tools from a skill

    Args:
        skill (Skills): Skill to make a tool from
        llm (BaseLanguageModel): LLM to use if the skill requires one
        executor (ExecuteCommands): MindsDB executor to use if the skill requires one

    Returns:
        tools (List[BaseTool]): List of tools for the given skill
    """
    if skill.type == 'text_to_sql':
        return _make_text_to_sql_tools(skill, llm, executor)
    raise NotImplementedError(f'skill of type {skill.type} is not supported as a tool')