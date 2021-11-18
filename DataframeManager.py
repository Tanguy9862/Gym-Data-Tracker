import pandas as pd


class DataframeManager:

    def __init__(self):
        pass

    def create_global_dataframe(self, table, user_id):

        all_exercises_performances = table.query.filter_by(user_id=user_id).all()

        # Create a DataFrame for all performances data :
        df_global_exercise_performance = pd.DataFrame(columns=['Date', 'Exercice', 'Performance globale', 'Notes', 'Sommeil'])

        for exercise_performance in all_exercises_performances:
            new_row = {
                "Date": exercise_performance.date_performance,
                "Exercice": exercise_performance.exercise.exercise_name.title(),
                "Performance globale": exercise_performance.global_performance,
                "Notes": exercise_performance.notes,
                "Sommeil": exercise_performance.sleep_time
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

    def generate_strength_df_for_plot(self, all_performances_current_exercise):

        print(all_performances_current_exercise)

        # Create a DataFrame
        df_exercise = pd.DataFrame(columns=['Date', 'Charge', 'Répétitions'])

        # Add data to the df_exercise DataFrame
        for performance in all_performances_current_exercise:
            if performance.three_reps != "":
                df_exercise = df_exercise.append({'Date': performance.date_performance,
                                                  'Charge': performance.three_reps,
                                                  'Répétitions': 3}, ignore_index=True)
            if performance.two_reps != "":
                df_exercise = df_exercise.append({'Date': performance.date_performance,
                                                  'Charge': performance.two_reps,
                                                  'Répétitions': 2}, ignore_index=True)
            if performance.one_reps != "":
                df_exercise = df_exercise.append({'Date': performance.date_performance,
                                                  'Charge': performance.one_reps,
                                                  'Répétitions': 1}, ignore_index=True)


        # Convert columns to respected dtypes
        df_exercise['Date'] = pd.to_datetime(arg=df_exercise['Date'], format='%Y/%m/%d')
        df_exercise['Charge'] = pd.to_numeric(arg=df_exercise['Charge'])
        df_exercise['Répétitions'] = pd.to_numeric(arg=df_exercise['Répétitions'])

        return df_exercise

    def generate_endurance_df_for_plot(self, all_performances_current_exercise):

        print(all_performances_current_exercise)

        # Create a DataFrame
        df_exercise = pd.DataFrame(columns=['Date', 'Charge', 'Répétitions'])

        # Add data to the df_exercise DataFrame
        for performance in all_performances_current_exercise:
            if performance.twenty_reps != "":
                df_exercise = df_exercise.append({'Date': performance.date_performance,
                                                  'Charge': performance.twenty_reps,
                                                  'Répétitions': 20}, ignore_index=True)
            if performance.fifteen_reps != "":
                df_exercise = df_exercise.append({'Date': performance.date_performance,
                                                  'Charge': performance.fifteen_reps,
                                                  'Répétitions': 15}, ignore_index=True)

            if performance.ten_reps != "":
                df_exercise = df_exercise.append({'Date': performance.date_performance,
                                                  'Charge': performance.ten_reps,
                                                  'Répétitions': 10}, ignore_index=True)


        # Convert columns to respected dtypes
        df_exercise['Date'] = pd.to_datetime(arg=df_exercise['Date'], format='%Y/%m/%d')
        df_exercise['Charge'] = pd.to_numeric(arg=df_exercise['Charge'])
        df_exercise['Répétitions'] = pd.to_numeric(arg=df_exercise['Répétitions'])

        return df_exercise


