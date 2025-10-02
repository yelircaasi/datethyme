# import the Date class from the package datethyme
from datethyme import Date


# the 'parse' method reads a string containing a date
#   in the format yyyy-mm-dd
date_young = Date.parse("1993-06-15")
date_almost_young = Date.parse("1992-10-15")
date_old = Date.parse("1989-01-18")

# def narrate(name: str, d: Date):
#     print(f"{name}'s life had a tragic beginning.")
#     print(f"{name} lost his foreskin on {d.pretty()}.")
#     print("RIP, foreskin.")


# print(f"Huhu's life had a tragic beginning.")
# print(f"Huhu lost his foreskin on {date_old.format("{Month3} {day}, {year}")}.")
# print("RIP, foreskin.")

# print(f"Fufu's life had a tragic beginning.")
# print(f"Fufu lost his foreskin on {date_almost_young.format("{Month3} {day}, {year}")}.")
# print("RIP, foreskin.")

# print(f"Isaac's life had a tragic beginning.")
# print(f"Isaac lost his foreskin on {date_young.format("{Month3} {day}, {year}")}.")
# print("RIP, foreskin.")

def narrate(name: str, d: Date, male: bool):
    pronoun = "his" if male else "her"
    adjective = "tragic" if male else "happy"
    print(f"{name}'s life had a {adjective} beginning.")
    if male:
        print(f"{name} lost {pronoun} foreskin on {d.format("{Month3} {day}, {year}")}.")
        print("RIP, foreskin.")
    else:
        print(f"{name} popped out of her mama on {d.format("{Month3} {day}, {year}")}.")
    print()

    return "I am the great Cornholio"



def calculate_bmi(height_weight_pairs: list[tuple[float, float]]) -> list[float]:
    return [round(w / (h ** 2), 2) for h, w in height_weight_pairs]


def average(numbers: list[float]) -> float:
    return round(sum(numbers) / len(numbers), 2)


hw_pairs = [
    (1.78, 74.5),
    (2.05, 92.3),
    (1.66, 78.0)
]

bmis = calculate_bmi(hw_pairs)
average_bmi = average(bmis)
print(f"The average BMI is {average_bmi}. Well done, skinny bitches!")


huhu_output = narrate("Huhu", date_old, False)
fufu_output = narrate("Fufu", date_almost_young, False)
susu_output = narrate("Susu", date_young, True)

print(huhu_output)
print(fufu_output)
print(susu_output)








import pandas as pd
import sklearn

df = pd.read_csv("patient_info.csv")

median_height = df["height"].median()
average_height = df["height"].mean()

print(f"The median height is {median_height}")
print(f"The average height is {average_height}")

df.height.groupby("age").mean()


X = sklearn.dataset("")
new_x = [...]
linreg = sklearn.LinearModel()
linreg.fit(X)
linreg.predict(new_x)

# age   |   mean height
#   2   |   0.65
#   3   |   0.68
# ...
