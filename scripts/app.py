import bmi

people = [
    {"name": "Alice", "height": 1.65, "weight": 60},
    {"name": "Bob", "height": 1.80, "weight": 85},
    {"name": "Carla", "height": 1.70, "weight": 70},
    {"name": "David", "height": 1.75, "weight": 78},
    {"name": "Elena", "height": 1.60, "weight": 55},
    {"name": "Frank", "height": 1.85, "weight": 95},
    {"name": "Grace", "height": 1.68, "weight": 62},
    {"name": "Hassan", "height": 1.78, "weight": 80},
]

for person in people:
    print(person)
    weight = person["weight"]
    height = person["height"]
    bmi_value = bmi.compute_bmi(weight, height)
    category = bmi.classify_bmi(bmi_value)
    print(f"{person['name']}'s BMI is {bmi_value:.2f}, which is classified as {category}.")
    print()

