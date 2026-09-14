def get_input(prompt, input_type=float):
    while True:
        try:
            return input_type(input(f"{prompt}: "))
        except ValueError:
            print("Please enter a valid number.")

def calculate_recovery(data):
    score = 100

    # RHR
    if data["rhr"] > 70:
        score -= 10
    elif data["rhr"] < 55:
        score += 5

    # HRV
    if data["hrv"] < 50:
        score -= 15
    elif data["hrv"] > 80:
        score += 10

    # Convert sleep phases from % to hours
    deep_hours = data["sleep_total"] * (data["deep_percent"] / 100)
    rem_hours = data["sleep_total"] * (data["rem_percent"] / 100)

    # Sleep
    if data["sleep_total"] < 6:
        score -= 15
    elif data["sleep_total"] > 8:
        score += 5

    if deep_hours < 1:
        score -= 10
    if rem_hours < 1:
        score -= 5

    # Exercise
    if data["exercise_intensity"] == 3:
        score -= 20
    elif data["exercise_intensity"] == 2:
        score -= 10
    elif data["exercise_intensity"] == 1:
        score -= 5

    # General well-being
    score -= (10 - data["energy_level"]) * 0.5
    score -= (10 - data["focus_level"]) * 0.5
    score -= data["stress_level"] * 0.5

    score = max(0, min(score, 100))
    return round(score)

def main():
    print("🔥 Recovery Score Tracker - Huawei Sleep Mode 🔥\n")

    data = {}
    print("💪 Exercise:")
    print("0 - None\n1 - Light\n2 - Moderate\n3 - Intense")
    data["exercise_intensity"] = get_input("Choose exercise intensity", int)

    print("\n❤️ Biometrics:")
    data["rhr"] = get_input("Resting Heart Rate (RHR)")
    data["hrv"] = get_input("Heart Rate Variability (HRV, enter 50 if unknown)")

    print("\n😴 Sleep Data (from Huawei Health %):")
    data["sleep_total"] = get_input("Total sleep hours")
    data["deep_percent"] = get_input("Deep sleep percentage (%)")
    data["rem_percent"] = get_input("REM sleep percentage (%)")
    data["sleep_score"] = get_input("Sleep Score (enter 70 if not available)")

    print("\n🧠 Mental State:")
    data["energy_level"] = get_input("Energy level (1–10)", int)
    data["focus_level"] = get_input("Focus level (1–10)", int)
    data["stress_level"] = get_input("Stress level (1–10)", int)

    recovery_score = calculate_recovery(data)

    print("\n✅ Recovery Result:")
    print(f"Your recovery score: {recovery_score}%")

    if recovery_score >= 80:
        print("🔥 You're fully recovered and ready to crush your workout!")
    elif recovery_score >= 50:
        print("⚠️ Moderate recovery – go easy or focus on active recovery.")
    else:
        print("🛌 Poor recovery – rest and recharge today.")

if __name__ == "__main__":
    main()
