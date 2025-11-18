import os
from neo4j import GraphDatabase
from openai import OpenAI
from dotenv import load_dotenv

def main():
    """Основная функция приложения"""
    load_dotenv()
    
    # Инициализация клиентов
    client = init_openai_client()
    driver = init_neo4j_driver()
    
    try:
        # Создание тестовых данных
        create_sample_data(driver)
        
        # Пользовательский запрос
        user_query = "Как Эйнштейн связан с квантовой теорией поля?"
        entity_to_search = "Albert Einstein"
        
        # Получение контекста из графа знаний
        kg_context = build_kg_context(driver, entity_to_search)
        
        print("Контекст из KG:")
        print(kg_context)
        print("\n" + "="*60 + "\n")
        
        # Генерация ответа
        answer = generate_answer(client, kg_context, user_query)
        
        print("Ответ модели:")
        print(answer)
        
    finally:
        # Всегда закрываем соединение
        driver.close()

def init_openai_client():
    """Инициализация клиента OpenAI"""
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

def init_neo4j_driver():
    """Инициализация драйвера Neo4j"""
    return GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", os.getenv("NEO4J_PASSWORD", "password"))
    )

def query_kg(tx, entity_name: str):
    """Запрос к графу знаний"""
    result = tx.run(
        """
        MATCH (n {name: $name})-[r]->(m)
        RETURN 
            labels(n)[0] AS source_label,
            n.name AS source,
            type(r) AS relationship,
            labels(m)[0] AS target_label,
            coalesce(m.name, m.title, id(m)) AS target
        LIMIT 20
        """,
        name=entity_name
    )
    return list(result)

def build_kg_context(driver, entity_name: str) -> str:
    """Построение контекста из графа знаний"""
    with driver.session() as session:
        records = session.execute_read(query_kg, entity_name)
    
    if not records:
        return f"В графе знаний ничего не найдено про «{entity_name}»."
    
    lines = []
    for r in records:
        line = f"{r['source']} → {r['relationship']} → {r['target']}"
        lines.append(line)
    
    return "Из графа знаний известно:\n" + "\n".join(lines)

def create_sample_data(driver):
    """Создание тестовых данных"""
    with driver.session() as session:
        session.execute_write(lambda tx: tx.run("""
            MERGE (a:Person {name: "Albert Einstein"})
            MERGE (b:Theory {name: "Специальная теория относительности"})
            MERGE (c:Theory {name: "Общая теория относительности"})
            MERGE (d:Theory {name: "Квантовая механика"})
            MERGE (e:Person {name: "Нильс Бор"})
            MERGE (a)-[:РАЗРАБОТАЛ]->(b)
            MERGE (a)-[:РАЗРАБОТАЛ]->(c)
            MERGE (a)-[:ВЛИЯЛ_НА]->(d)
            MERGE (a)-[:СПОРИЛ_С]->(e)
            MERGE (e)-[:РАЗРАБОТАЛ]->(d)
        """))

def generate_answer(client, kg_context: str, user_query: str) -> str:
    """Генерация ответа с помощью LLM"""
    prompt = f"""Ты — эксперт по истории физики. Отвечай только на основе фактов из графа знаний ниже.
Не придумывай ничего дополнительно.

Факты из графа знаний:
{kg_context}

Вопрос: {user_query}
Ответь кратко и точно."""

    response = client.chat.completions.create(
        model="anthropic/claude-3.5-sonnet",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    main()