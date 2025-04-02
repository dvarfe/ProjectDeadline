# Typing
Hours = int
Points = int
Image = ...


class Task:
    def __init__(self, name: str, description: str, image: Image,
                 difficulty: Hours, award: Points, penalty: Points,
                 event_on_success: callable, event_on_fail: callable):
        """
        A task that can be given to a player

        :param name: Task name
        :param description: Task description
        :param image: Task image
        :param difficulty: The number of hours required to complete the task
        :param award: The number of points awarded for completing the task
        :param penalty: The number of points taken away if the task is failed
        :param event_on_success: An event that occurs if the task is completed
        :param event_on_fail: An event that occurs if the task is failed
        """
        self.name = name
        self.description = description
        self.image = image
        self.difficulty = difficulty
        self.award = award
        self.penalty = penalty
        self.event_on_success = event_on_success
        self.event_on_fail = event_on_fail
