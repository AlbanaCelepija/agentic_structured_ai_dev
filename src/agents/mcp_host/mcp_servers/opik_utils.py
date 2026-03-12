import os
import opik
from loguru import logger
from opik.configurator.configure import OpikConfigurator
from settings import settings


def configure() -> None:
    if settings.OPIK_PROJECT_NAME:
        try:
            os.environ["OPIK_PROJECT_NAME"] = settings.OPIK_PROJECT_NAME
            # opik.configure(
            #    workspace=default_workspace,
            #    use_local=False,
            #    force=True,
            # )
            logger.info(
                f"Opik configured successfully using workspace '{default_workspace}'"
            )
        except Exception:
            logger.warning(
                "Couldn't configure Opik. There is probably a problem with the OPIK_PROJECT_NAME environment variables or with the Opik server."
            )


def get_dataset(name: str) -> opik.Dataset | None:
    client = opik.Opik()
    try:
        dataset = client.get_dataset(name=name)
    except Exception:
        dataset = None

    return dataset


def create_dataset(name: str, description: str, items: list[dict]) -> opik.Dataset:
    client = opik.Opik()

    client.delete_dataset(name=name)

    dataset = client.create_dataset(name=name, description=description)
    dataset.insert(items)

    return dataset
