"""
statistical analysis
Martin and Daniel
"""
from neighbourhood_crime import NeighbourhoodCrimeOccurrences, NeighbourhoodCrimePIndex, NeighbourhoodCrime
from sklearn.linear_model import LinearRegression
import numpy as np
import plotly.graph_objects as go
import math


def gen_linear_regression(occurences: NeighbourhoodCrimeOccurrences, month: int,
                          include: list[int]) -> LinearRegression:
    """Print the linear regression for this data for the given month."""
    # Initialize the model
    model = LinearRegression()

    raw_data = occurences.get_occurrences(month)
    x_train = [[t[0]] for t in raw_data if t[0] in include]
    y_train = [t[1] for t in raw_data if t[0] in include]

    # Train the model
    model.fit(x_train, y_train)

    return model


#         # Print the model.
#         print("h(x) = {} + {}*x".format(np.round(model.intercept_, 3), np.round(model.coef_[0], 3)))

#         # Get points for the line
#         lower = x_train[0][0] - 1
#         min_val = lower * model.coef_[0] + model.intercept_
#         upper = x_train[-1][0] + 1
#         max_val = upper * model.coef_[0] + model.intercept_

#         # Create the figure
#         scatter1 = go.Scatter(x=[t[0] for t in raw_data], y=y_train, mode='markers',
#                               name=f'{self.neighbourhood} occurrences', fillcolor='green')
#         scatter2 = go.Scatter(x=[lower, upper], y=[min_val, max_val], mode='lines',
#                               name='Linear regression')

#         fig = go.Figure()
#         fig.add_trace(scatter1)
#         fig.add_trace(scatter2)

#         # Configure the figure
#         fig.update_layout(title=f'Linear regression of number of occurrences of {self.crime_type} '
#                                 f'in {self.neighbourhood} in {self.month_to_str(month)}',
#                           xaxis_title='Year', yaxis_title='Num occurrences')

#         # Show the figure in the browser
#         fig.show()
def gen_error(occurences: NeighbourhoodCrimeOccurrences, month: int, include: list[int],
              model: LinearRegression) -> float:
    """Return the error of the linear regression given the month of the data
    and years that should be excluded from the calculation.
    Thus method uses the RMSE."""
    squared_sum, count = 0, 0

    for x, y in occurences.get_occurrences(month):
        if x in include:
            squared_sum += (y - model.predict(x)) ** 2
            count += 1

    return math.sqrt(squared_sum / count)


def gen_z(observation: float, prediction: float, standard_deviation: float) -> tuple[float, bool]:
    """
    Generate a tuple containing:
     - A z-value based on the model's prediction and the actual observation. (How many standard
     deviations off the prediction was from the actual value)
     - Whether or not the model overestimated the result (meaning the actual value is
     less than the predicted value).

     Preconditions:
        - standard_deviation > 0

    >>> z1, overestimated1 = gen_z(5.0, 3.0, 1.0)
    >>> math.isclose(z1, 2.0) and not overestimated1
    True

    >>> z2, overestimated2 = gen_z(998.9, 1000.0, 5.0)
    >>> math.isclose(z2, 0.22) and overestimated2
    True
    """
    # Whether or not the observation was overestimated
    overestimated = False

    # How far off the prediction was from the observation
    deviation = observation - prediction

    # Calculate z, how many standard deviations off the prediction was.
    z = abs(deviation) / standard_deviation

    # if the observation is less than the prediction...
    if observation < prediction:
        # the observation was overestimated.
        overestimated = True

    return (z, overestimated)


def gen_p(z: float) -> float:
    """
    Generates p, the probability that the model would have predicted a result as least as extreme as
    that observed. A low p value indicates a low chance the observed result would be a predicted,
    meaning the model is likely innacurate.

    Preconditions:
        - z >= 0

    Use the empirical rule to test the correctness of the function (rounding to 1 decimal place):
    >>> p1 = gen_p(1)
    >>> math.isclose(p1 * 100, 100 - 68.27, abs_tol=0.05)
    True
    >>> p2 = gen_p(2)
    >>> math.isclose(p2 * 100, 100 - 95.45, abs_tol=0.05)
    True
    >>> p3 = gen_p(3)
    >>> math.isclose(p3 * 100, 100 - 99.74, abs_tol=0.05)
    True
    """
    # Cite function!
    p = 1 - math.erf(z / (2 ** (1 / 2)))

    return p


def gen_pindex(p: float, overestimated: bool) -> float:
    """
    Generate the index based on 1 - p to measure the effect of COVID-19 on crime counts by
    converting it into a percentage from a decimal.

    (provide example)

    Preconditions:
        - 0 <= p < 1

    >>> pindex1 = gen_pindex(0.1, False)
    >>> math.isclose(pindex1, 90.0)
    True

    >>> pindex2 = gen_pindex(0.7, True)
    >>> math.isclose(pindex2, -30.0)
    True
    """
    pindex = (1 - p) * 100

    if overestimated:
        pindex *= -1

    return pindex
