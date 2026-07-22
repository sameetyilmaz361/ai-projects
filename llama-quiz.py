import os
from llama_cpp import Llama

script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "slm.gguf")

model = Llama(model_path=model_path, n_ctx=512, verbose=False)

topic = input("Enter a topic: ").strip()
while len(topic) == 0:
    topic = input("Topic cannot be empty. Enter a topic: ").strip()

score = 0

for i in range(3):
    print(f"\n--- Question {i + 1} / 3 ---")

    response = model.create_chat_completion(
        messages=[
            {"role": "system",
             "content": "Generate a multiple choice question "
                        "with 4 options (A, B, C, D). "
                        "Write the correct answer at the end "
                        "as 'Answer: X'."},
            {"role": "user", "content": topic},
        ],
        max_tokens=256,
        temperature=0.9,
    )
    quiz_text = response["choices"][0]["message"]["content"]
    print(quiz_text)

    correct = "?"
    for line in quiz_text.split("\n"):
        if "Answer:" in line:
            correct = line.split("Answer:")[-1].strip()[0].upper()
            break

    user_answer = input("\nYour answer (A/B/C/D): ").strip().upper()

    if correct == "?":
        print("Could not determine the correct answer from the model's output — skipping this question.")
        continue

    if user_answer == correct:
        print("Correct!")
        score += 1
    else:
        print(f"Wrong! The correct answer was {correct}.")

print(f"\n{'=' * 30}")
print(f"Final score: {score} / 3")

if score == 3:
    print("Perfect!")
elif score >= 2:
    print("Good job!")
else:
    print("Keep studying!")