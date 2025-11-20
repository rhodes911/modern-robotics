"""Quick test script for RAG chatbot"""
import subprocess
import sys

questions = [
    "What is forward kinematics?",
    "Explain the product of exponentials formula",
    "What is the Jacobian matrix used for?",
    "Explain Grubler's formula for degrees of freedom"
]

print("=" * 70)
print("Testing Modern Robotics RAG Chatbot")
print("=" * 70)

for i, question in enumerate(questions, 1):
    print(f"\n{'=' * 70}")
    print(f"Question {i}: {question}")
    print('=' * 70)
    
    # Create input with question + quit
    input_text = f"{question}\nquit\n"
    
    # Run chatbot with the question
    process = subprocess.Popen(
        [sys.executable, "rag_chatbot.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    output, errors = process.communicate(input=input_text)
    
    # Extract just the answer section
    lines = output.split('\n')
    in_answer = False
    answer_lines = []
    
    for line in lines:
        if '📝 Answer:' in line:
            in_answer = True
            continue
        if in_answer:
            if '------' in line:
                if answer_lines:  # Second dash means end of answer
                    break
                continue
            if '📚 Sources' in line:
                break
            answer_lines.append(line)
    
    answer = '\n'.join(answer_lines).strip()
    print(f"\n{answer}\n")

print("\n" + "=" * 70)
print("Test Complete!")
print("=" * 70)
