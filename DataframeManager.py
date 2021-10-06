import pandas as pd


class DataframeManager:

    def __init__(self):
        pass

    def create_global_dataframe(self, table, user_id):
        self.all_exercises_performances = table.query.filter_by(user_id=user_id).all()

        # Create an empty DataFrame for all performances data :
        df_global_exercise_performance = pd.DataFrame(
            {
                'Date': [],
                'Exercice': [],
                'Performance globale': [],
                # 'three_reps': [],
                # 'two_reps': [],
                # 'one_reps': [],
                # 'ten_reps': [],
                # 'fifteen_reps': [],
                # 'twenty_reps': [],
            }
        )

        for exercise_performance in self.all_exercises_performances:
            new_row = {
                "Date": exercise_performance.date_performance,
                "Exercice": exercise_performance.exercise.exercise_name.title(),
                "Performance globale": exercise_performance.global_performance,
                # "three_reps": exercise_performance.three_reps,
                # "two_reps": exercise_performance.two_reps,
                # "one_reps": exercise_performance.one_reps,
                # "ten_reps": exercise_performance.ten_reps,
                # "fifteen_reps": exercise_performance.fifteen_reps,
                # "twenty_reps": exercise_performance.twenty_reps
            }
            df_global_exercise_performance = df_global_exercise_performance.append(new_row, ignore_index=True)
        return df_global_exercise_performance


    def create_specific_dataframe(self, table, exercise_id):
        self.exercise = table.query.get(exercise_id)

        new_df = pd.DataFrame(
            {
                'performance_id': [],
                'Date': [],
                'Performance globale': [],
                'x3@RPE': [],
                'x2@RPE': [],
                'x1@RPE': [],
                'x10': [],
                'x15': [],
                'x20': [],
            }
        )

        for n in range(len(self.exercise.performance)):
            new_row = {
                "performance_id": str(self.exercise.performance[n].id).split(".")[0],
                "Date": self.exercise.performance[n].date_performance,
                "Performance globale": self.exercise.performance[n].global_performance,
                "x3@RPE": f"{self.exercise.performance[n].three_reps}@{self.exercise.performance[n].three_rpe}",
                "x2@RPE": f"{self.exercise.performance[n].two_reps}@{self.exercise.performance[n].two_rpe}",
                "x1@RPE": f"{self.exercise.performance[n].one_reps}@{self.exercise.performance[n].one_rpe}",
                "x10": self.exercise.performance[n].ten_reps,
                "x15": self.exercise.performance[n].fifteen_reps,
                "x20": self.exercise.performance[n].twenty_reps
            }
            new_df = new_df.append(new_row, ignore_index=True)

        return new_df
