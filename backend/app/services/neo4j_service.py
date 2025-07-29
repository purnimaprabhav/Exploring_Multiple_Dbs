from backend.app.config.db.neo4j_conn import get_session
from typing import List

def get_user_by_username(username: str):
    query = """
    MATCH (u:User {username: $username})
    RETURN u
    """
    with get_session() as session:
        result = session.run(query, username=username)
        record = result.single()
        if not record:
            return None
        u = record["u"]
        return {
            "username": u.get("username", ""),
            "name": u.get("name", ""),
            "number": u.get("number", ""),
            "email": u.get("email", ""),
            "role": u.get("role", ""),
            "skills": u.get("skills", []),
            "interests": u.get("interests", []),
            "experience": u.get("experience", 0),
            "organization": u.get("organization", ""),
            "availability": u.get("availability", False)
        }

def check_user_exists(username: str) -> bool:
    query = "MATCH (u:User {username: $username}) RETURN u.username LIMIT 1"
    with get_session() as session:
        result = session.run(query, {"username": username}).single()
        return result is not None

def create_user(user) -> bool:
    query = """
    CREATE (u:User {
        username: $username,
        name: $name,
        number: $number,
        email: $email,
        role: $role,
        experience: $experience,
        organization: $organization,
        availability: $availability
    })
    WITH u
    FOREACH (skill IN $skills | MERGE (s:Skill {name: skill}) MERGE (u)-[:HAS_SKILL]->(s))
    FOREACH (interest IN $interests | MERGE (i:Interest {name: interest}) MERGE (u)-[:HAS_INTEREST]->(i))
    """
    with get_session() as session:
        session.run(query, **user.dict())
    return True

def update_availability(username: str, availability: bool) -> bool:
    with get_session() as session:
        result = session.run("""
            MATCH (u:User {username: $username})
            SET u.availability = $availability
            RETURN u
        """, username=username, availability=availability)
        return result.single() is not None

def find_matching_users(role: str, skills: List[str], min_exp: int):
    with get_session() as session:
        query = """
        MATCH (u:User)
        WHERE ($role IS NULL OR u.role = $role)
          AND u.experience >= $min_exp
          AND u.availability = true
        OPTIONAL MATCH (u)-[:HAS_SKILL]->(s:Skill)
        WHERE size($skills) = 0 OR s.name IN $skills
        WITH u, collect(DISTINCT s.name) as skill_names
        RETURN {
            username: u.username,
            name: u.name,
            role: u.role,
            experience: u.experience,
            availability: u.availability,
            email: u.email,
            number: u.number,
            skills: skill_names
        } AS user
        """
        result = session.run(query, {
            "role": role,
            "skills": skills,
            "min_exp": min_exp
        })
        return [record["user"] for record in result]

def get_contact(username: str):
    query = "MATCH (u:User {username: $username}) RETURN u.number AS number, u.email AS email"
    with get_session() as session:
        result = session.run(query, {"username": username}).single()
        return result.data() if result else None
