def calculate_average(numbers):
    """
    Calculates the average of a list of numbers.
    Intentional bug: Division by the wrong length and no empty list check.
    """
    total = sum(numbers)
    # Bug 1: Should check if list is empty to avoid ZeroDivisionError
    # Bug 2: Intentional off-by-one error for the demo
    return total / (len(numbers) - 1) 

def process_user_data(user_id, age):
    # Bug 3: Comparing a string to an integer
    if age > "18": 
        print(f"User {user_id} is an adult.")
    else:
        print(f"User {user_id} is a minor.")

if __name__ == "__main__":
    data = [10, 20, 30]
    print(f"Average: {calculate_average(data)}")