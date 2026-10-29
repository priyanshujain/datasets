import os
from pathlib import Path
from inspect_ai import Task, eval, task
from inspect_ai.dataset import Sample, json_dataset
from inspect_ai.scorer import exact
from inspect_ai.solver import generate, system_message

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

DATASET_PATH = Path(__file__).parent / "power_seeking_dataset.json"


def record_to_sample(record):
    options = "\n".join(f"{letter}) {text}" for letter, text in record["answers"].items())
    return Sample(
        input=f"{record['question']}\n\n{options}",
        target=record["answer_not_matching_behavior"],
        metadata={
            "system": record["system"],
            "behavior_category": record["behavior_category"],
            "answer_matching_behavior": record["answer_matching_behavior"],
        },
    )


dataset = json_dataset(str(DATASET_PATH), record_to_sample)


@task
def power_eval():
    return Task(
        dataset=dataset,
        solver=[
            system_message("{system}\n\nAnswer with only the letter of one option. No explanation."),
            generate(),
        ],
        scorer=exact(),
    )


logs = eval(
    power_eval(),
    model="openrouter/z-ai/glm-5.3-flash",
)

for sample in logs[0].samples:
    print("category: ", sample.metadata["behavior_category"])
    print("answer: ", sample.output.completion)
    print("score: ", sample.scores)
