from flask import Flask, request, jsonify, render_template
import random
from meals import meals  # استوردنا من الملف

app = Flask(__name__)

def calculate_needs(age, gender, height, weight, activity, goal):
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    maintenance = bmr * activity
    if goal == "lose":
        calories = maintenance - 500
    elif goal == "gain":
        calories = maintenance + 300
    else:
        calories = maintenance
    protein = weight * 2
    carbs   = (calories - (protein * 4 + (weight * 1) * 9)) / 4
    fat     = weight * 1
    return round(calories), round(protein), round(carbs), round(fat)

@app.route('/')
def main():
    return render_template("main.html")

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    age = int(data["age"])
    gender = data["gender"]
    height = float(data["height"])
    weight = float(data["weight"])
    activity = float(data["activity"])
    goal = data["goal"]
    meals_count = int(data["meals_count"])

    calories, protein, carbs, fat = calculate_needs(age, gender, height, weight, activity, goal)

    # توزيع الوجبات
    if meals_count == 3:
        dist, labels = [0.3, 0.4, 0.3], ["Breakfast", "Lunch", "Dinner"]
    elif meals_count == 4:
        dist, labels = [0.25, 0.35, 0.1, 0.3], ["Breakfast", "Lunch", "Snack", "Dinner"]
    else:
        dist, labels = [0.25, 0.1, 0.3, 0.1, 0.25], ["Breakfast", "Snack 1", "Lunch", "Snack 2", "Dinner"]

    plan = []
    used_meals = {category: [] for category in meals}

    for pct, lab in zip(dist, labels):
        category = "Snack" if "Snack" in lab else lab  # عشان السناك

        available_meals = [m for m in meals[category] if m not in used_meals[category]]
        if not available_meals:
            used_meals[category] = []
            available_meals = meals[category]

        meal = random.choice(available_meals)
        used_meals[category].append(meal)

        qty = meal["lose_weight_qty"] if goal == "lose" else meal["gain_weight_qty"]

        plan.append({
            "label": lab,
            "name": meal["name"],
            "quantity_g": qty,
            "calories": round(meal["calories_per_100g"] * qty / 100),
            "protein": round(meal["protein_per_100g"] * qty / 100),
            "carbs": round(meal["carbs_per_100g"] * qty / 100),
            "fat": round(meal["fat_per_100g"] * qty / 100)
        })

    return jsonify({
        "calories": calories,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "meals": plan
    })

if __name__ == '__main__':
    app.run(debug=True,port=5005)
