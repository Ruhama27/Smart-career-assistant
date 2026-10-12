import math

#Precision = Relevant Recommendations/ Total Recommendations
        
def precision(recommended, relevant):

    recommended = set(recommended)

    relevant = set(relevant)

    if len(recommended) == 0:
        return 0

    correct = recommended.intersection(relevant)

    return len(correct) / len(recommended)

#Recall=Relevant Recommendations/Total Relevant Items

def recall(recommended, relevant):

    recommended = set(recommended)

    relevant = set(relevant)

    if len(relevant) == 0:
        return 0

    correct = recommended.intersection(relevant)

    return len(correct) / len(relevant)

#RMSE=√(Average Squared Error)
def rmse(actual, predicted):

    if len(actual) != len(predicted):

        return None

    error = 0

    for a, p in zip(actual, predicted):

        error += (a - p) ** 2

    mse = error / len(actual)

    return math.sqrt(mse)

if __name__ == "__main__":

    recommended = ["I001", "I002", "I003", "I004"]

    relevant = ["I001", "I003", "I005"]

    actual = [5, 4, 3, 5]

    predicted = [4.8, 4.2, 2.7, 4.9]

    print("Precision :", round(precision(recommended, relevant), 2))

    print("Recall :", round(recall(recommended, relevant), 2))

    print("RMSE :", round(rmse(actual, predicted), 2))