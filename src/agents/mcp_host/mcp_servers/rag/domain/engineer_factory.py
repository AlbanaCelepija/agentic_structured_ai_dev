from rag_assistant.start_simple_evolve.mcp_host.mcp_servers.rag.domain import Engineer

ENGINEER_NAMES = {
    "fairness": "FairnessEngineer",
    "robustness": "RobustnessEngineer",
}
AVAILABLE_ENGINEERS = list(ENGINEER_NAMES.keys())


class EngineersFactory:
    @staticmethod
    def get_philosopher(id: str) -> Philosopher:
        """Creates a philosopher instance based on the provided ID.

        Args:
            id (str): Identifier of the philosopher to create

        Returns:
            Philosopher: Instance of the philosopher

        Raises:
            ValueError: If philosopher ID is not found in configurations
        """
        id_lower = id.lower()

        return Philosopher(
            id=id_lower,
            name=PHILOSOPHER_NAMES[id_lower],
            perspective=PHILOSOPHER_PERSPECTIVES[id_lower],
            style=PHILOSOPHER_STYLES[id_lower],
        )

    @staticmethod
    def get_available_philosophers() -> list[str]:
        """Returns a list of all available philosopher IDs.

        Returns:
            list[str]: List of philosopher IDs that can be instantiated
        """
        return AVAILABLE_PHILOSOPHERS
