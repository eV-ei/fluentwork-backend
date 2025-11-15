from models import Scenario, ComplexityLevel, UserProgress
import random


# All available scenarios
SCENARIOS = [
    # EASY scenarios - Basic status updates
    Scenario(
        id="easy_1",
        primary_topic="weekly_progress",
        complexity_level=ComplexityLevel.EASY,
        context="You had a productive week and completed your assigned tasks.",
        initial_prompt="Hi! How was your week? What did you work on?",
        helpful_phrases=[
            "I completed...",
            "I'm currently working on...",
            "This week I focused on...",
            "Everything is on track."
        ]
    ),
    Scenario(
        id="easy_2",
        primary_topic="current_tasks",
        complexity_level=ComplexityLevel.EASY,
        context="You're working on updating the user dashboard with new analytics.",
        initial_prompt="Good morning! What are you currently working on?",
        helpful_phrases=[
            "I'm working on...",
            "I'm updating the...",
            "I'm making progress on...",
            "I should finish this by..."
        ]
    ),

    # MEDIUM scenarios - Issues and blockers
    Scenario(
        id="medium_1",
        primary_topic="minor_delay",
        complexity_level=ComplexityLevel.MEDIUM,
        surprise_element="Manager asks about impact on timeline",
        context="Your task is delayed by 2 days because of API documentation issues.",
        initial_prompt="Hey, how's the API integration going?",
        helpful_phrases=[
            "I'm running into...",
            "There's a delay because...",
            "It will take an extra... days",
            "I estimate I'll finish by..."
        ]
    ),
    Scenario(
        id="medium_2",
        primary_topic="need_clarification",
        complexity_level=ComplexityLevel.MEDIUM,
        surprise_element="Manager asks you to propose a solution",
        context="You're unclear about the requirements for the new feature.",
        initial_prompt="I wanted to check in on the new feature. How's it coming along?",
        helpful_phrases=[
            "I need clarification on...",
            "I'm not sure about...",
            "Could we discuss...",
            "I have a question about..."
        ]
    ),
    Scenario(
        id="medium_3",
        primary_topic="cross_team_dependency",
        complexity_level=ComplexityLevel.MEDIUM,
        surprise_element="Manager asks when you followed up with other team",
        context="You're waiting on the design team to finalize mockups.",
        initial_prompt="What's the status on the homepage redesign?",
        helpful_phrases=[
            "I'm waiting for...",
            "I'm blocked by...",
            "Once I receive... I can proceed",
            "I followed up with... team"
        ]
    ),
    Scenario(
        id="medium_4",
        primary_topic="technical_blocker",
        complexity_level=ComplexityLevel.MEDIUM,
        surprise_element="Manager asks if you need additional resources",
        context="You're stuck on a performance issue with database queries.",
        initial_prompt="How's the database optimization task going?",
        helpful_phrases=[
            "I'm stuck on...",
            "I'm facing a challenge with...",
            "I could use some help with...",
            "I've tried... but..."
        ]
    ),

    # HARD scenarios - Complex situations requiring careful communication
    Scenario(
        id="hard_1",
        primary_topic="significant_delay",
        complexity_level=ComplexityLevel.HARD,
        surprise_element="Manager reveals client is waiting on this deliverable",
        context="Your feature is 5 days behind schedule due to unexpected technical challenges.",
        initial_prompt="I need an update on the payment integration. The deadline is approaching.",
        helpful_phrases=[
            "Unfortunately, we're behind schedule because...",
            "I've encountered unexpected...",
            "My revised estimate is...",
            "Here's what I'm doing to catch up..."
        ]
    ),
    Scenario(
        id="hard_2",
        primary_topic="scope_creep",
        complexity_level=ComplexityLevel.HARD,
        surprise_element="Manager suggests adding even more features",
        context="Stakeholders keep requesting additional features beyond the original scope.",
        initial_prompt="How's the customer portal coming? I heard marketing had some ideas.",
        helpful_phrases=[
            "We're getting requests for...",
            "This is beyond the original scope",
            "If we add this, it will impact...",
            "I suggest we prioritize..."
        ]
    ),
    Scenario(
        id="hard_3",
        primary_topic="need_help",
        complexity_level=ComplexityLevel.HARD,
        surprise_element="Manager asks why you didn't mention this earlier",
        context="You've been struggling with a complex algorithm for 3 days and need senior help.",
        initial_prompt="How's the search algorithm refactoring going? You've been on it for a while.",
        helpful_phrases=[
            "I need assistance with...",
            "I've been struggling with...",
            "Could someone review...",
            "I'd appreciate guidance on..."
        ]
    ),
    Scenario(
        id="hard_4",
        primary_topic="conflicting_priorities",
        complexity_level=ComplexityLevel.HARD,
        surprise_element="Manager adds another urgent task",
        context="You have three high-priority tasks and can't complete them all on time.",
        initial_prompt="Quick check-in. What are you focusing on this week?",
        helpful_phrases=[
            "I'm currently juggling...",
            "I need help prioritizing...",
            "Which should I focus on first?",
            "I can't complete all of these by..."
        ]
    ),
    Scenario(
        id="hard_5",
        primary_topic="quality_vs_speed",
        complexity_level=ComplexityLevel.HARD,
        surprise_element="Manager emphasizes quality importance after you mention rushing",
        context="You can meet the deadline but the code quality will suffer, or take 2 more days for proper implementation.",
        initial_prompt="The demo is in 3 days. Is everything ready?",
        helpful_phrases=[
            "I can meet the deadline, but...",
            "There's a trade-off between...",
            "If we want quality, we need...",
            "I recommend we..."
        ]
    ),

    # Additional EASY scenario
    Scenario(
        id="easy_3",
        primary_topic="completed_task",
        complexity_level=ComplexityLevel.EASY,
        context="You just finished implementing the login page and it's ready for review.",
        initial_prompt="Hi! I saw you closed the ticket. How did it go?",
        helpful_phrases=[
            "I finished...",
            "It's ready for review",
            "I implemented...",
            "It went smoothly"
        ]
    ),

    # Additional MEDIUM scenarios
    Scenario(
        id="medium_5",
        primary_topic="changing_requirements",
        complexity_level=ComplexityLevel.MEDIUM,
        surprise_element="Manager asks how this affects other features",
        context="The requirements changed mid-sprint and you need to revise your approach.",
        initial_prompt="How's the reports feature? I know the requirements were updated.",
        helpful_phrases=[
            "The requirements changed...",
            "I need to revise...",
            "This means I'll have to...",
            "I'm adjusting my approach"
        ]
    ),

    # Additional HARD scenario
    Scenario(
        id="hard_6",
        primary_topic="bug_in_production",
        complexity_level=ComplexityLevel.HARD,
        surprise_element="Manager asks about prevention measures",
        context="A bug you introduced is affecting production users, and you're working on a hotfix.",
        initial_prompt="I heard there's an issue in production. Can you update me?",
        helpful_phrases=[
            "There's a bug affecting...",
            "I'm working on a hotfix",
            "The issue is caused by...",
            "I'll have it fixed by..."
        ]
    ),
]


def get_scenarios_by_complexity(complexity: ComplexityLevel) -> list[Scenario]:
    """Get all scenarios matching a complexity level."""
    return [s for s in SCENARIOS if s.complexity_level == complexity]


def select_scenario_for_user(user_progress: UserProgress) -> Scenario:
    """
    Select appropriate scenario based on user progress.
    - Start with EASY scenarios for first 2 sessions
    - Move to MEDIUM after 2 successful easy sessions
    - Move to HARD after 4+ total sessions
    """
    if user_progress.total_sessions < 2:
        # First 2 sessions: always EASY
        available = get_scenarios_by_complexity(ComplexityLevel.EASY)
    elif user_progress.total_sessions < 5:
        # Sessions 3-5: MEDIUM
        available = get_scenarios_by_complexity(ComplexityLevel.MEDIUM)
    else:
        # Session 6+: Mix of MEDIUM and HARD
        if user_progress.total_sessions % 3 == 0:
            # Every 3rd session, use HARD
            available = get_scenarios_by_complexity(ComplexityLevel.HARD)
        else:
            # Otherwise MEDIUM
            available = get_scenarios_by_complexity(ComplexityLevel.MEDIUM)

    # Randomly select from available scenarios
    return random.choice(available)


def get_scenario_by_id(scenario_id: str) -> Scenario:
    """Get a specific scenario by ID."""
    for scenario in SCENARIOS:
        if scenario.id == scenario_id:
            return scenario
    raise ValueError(f"Scenario {scenario_id} not found")


def determine_next_complexity(user_progress: UserProgress) -> ComplexityLevel:
    """Determine the next complexity level for a user."""
    if user_progress.total_sessions < 2:
        return ComplexityLevel.EASY
    elif user_progress.total_sessions < 5:
        return ComplexityLevel.MEDIUM
    else:
        return ComplexityLevel.HARD
