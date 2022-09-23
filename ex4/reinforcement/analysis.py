# analysis.py
# -----------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

"""
  Muaz Abdeen & Alon Tifferet
"""


######################
# ANALYSIS QUESTIONS #
######################

# Change these default values to obtain the specified policies through
# value iteration.

def question2():
    answerDiscount = 0.9
    answerNoise = 0.0
    return answerDiscount, answerNoise


# =================================================

def question3a():
    """
    Prefer the close exit (+1), risking the cliff (-10)
    :return a 3-item tuple of (discount, noise, living reward)
             or the string 'NOT POSSIBLE'
    """
    answerDiscount = 0.2
    answerNoise = 0.0
    answerLivingReward = 0.0
    return answerDiscount, answerNoise, answerLivingReward
    # If not possible, return 'NOT POSSIBLE'


def question3b():
    """
    Prefer the close exit (+1), but avoiding the cliff (-10)
    :return a 3-item tuple of (discount, noise, living reward)
             or the string 'NOT POSSIBLE'
    """
    answerDiscount = 0.2
    answerNoise = 0.1
    answerLivingReward = 0.0
    return answerDiscount, answerNoise, answerLivingReward
    # If not possible, return 'NOT POSSIBLE'


def question3c():
    """
    Prefer the distant exit (+10), risking the cliff (-10)
    :return a 3-item tuple of (discount, noise, living reward)
             or the string 'NOT POSSIBLE'
    """
    answerDiscount = 0.9
    answerNoise = 0.0
    answerLivingReward = -0.5
    return answerDiscount, answerNoise, answerLivingReward
    # If not possible, return 'NOT POSSIBLE'


def question3d():
    """
    Prefer the distant exit (+10), avoiding the cliff (-10)
    :return a 3-item tuple of (discount, noise, living reward)
            or the string 'NOT POSSIBLE'
    """
    answerDiscount = 0.9
    answerNoise = 0.1
    answerLivingReward = 0.5
    return answerDiscount, answerNoise, answerLivingReward
    # If not possible, return 'NOT POSSIBLE'


def question3e():
    """
    Avoid both exits (also avoiding the cliff)
    :return a 3-item tuple of (discount, noise, living reward)
            or the string 'NOT POSSIBLE'
    """
    answerDiscount = 1.0
    answerNoise = 0.0
    answerLivingReward = 0.2
    return answerDiscount, answerNoise, answerLivingReward
    # If not possible, return 'NOT POSSIBLE'


# =================================================

def question6():
    # answerEpsilon = None
    # answerLearningRate = None
    # return answerEpsilon, answerLearningRate
    # If not possible, return 'NOT POSSIBLE'
    return 'NOT POSSIBLE'


if __name__ == '__main__':
    print('Answers to analysis questions:')
    import analysis

    for q in [q for q in dir(analysis) if q.startswith('question')]:
        response = getattr(analysis, q)()
        print('Question %s:\t%s' % (q, str(response)))
