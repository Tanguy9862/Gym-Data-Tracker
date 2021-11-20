import pandas as pd


class DataframeManager:

    def __init__(self):
        pass

    def create_dashboard_df(self, table, user_id):

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

    def create_global_df(self, all_performances):
        df = pd.DataFrame(columns=['Date', 'Performance globale', 'Notes'])

        for perf in all_performances:
            df = df.append({'Date': perf.date_performance,
                                          'Performance globale': perf.global_performance,
                                          'Notes': perf.notes,
                                          'Sommeil': perf.sleep_time},
                                         ignore_index=True)

        return df.sort_values(by='Date', ascending=False)

    def create_specific_df(self, highest_reps, all_performances, reps_range):
        """
        :param highest_reps: Highest value of repetition
        :param all_performances: List object of all_performances for an exercise
        :param reps_range: Min repetitions to max repetitions
        :return: Pandas DataFrame
        """
        df = pd.DataFrame(columns=['Date'])

        for reps in reps_range:
            if reps == 1:
                df[f'{reps} répétition'] = ""
            else:
                df[f'{reps} répétitions'] = ""

        for perf in all_performances:

            if perf.repetitions <= highest_reps:
                for reps in reps_range:
                    if reps == perf.repetitions and reps == 1:
                        df = df.append({
                            'Date': perf.date,
                            f'{reps} répétition': perf.weight
                        }, ignore_index=True)
                    elif reps == perf.repetitions and reps != 1:
                        df = df.append({
                            'Date': perf.date,
                            f'{reps} répétitions': perf.weight
                        }, ignore_index=True)

        df = df.fillna(0)
        df = df.groupby('Date').max().reset_index().replace(to_replace=0, value='-')

        return df.sort_values(by='Date', ascending=False)

    def create_df_for_plot(self, data_df, reps_range):
        df = pd.DataFrame(columns=['Date', 'Charge', 'Répétitions'])

        for index, row in data_df.iterrows():
            for reps in reps_range:
                if reps == 1:
                    if row[f'{reps} répétition'] != "-":
                        df = df.append({
                            'Date': row['Date'],
                            'Charge': row[f'{reps} répétition'],
                            'Répétitions': reps
                        }, ignore_index=True)
                else:
                    if row[f'{reps} répétitions'] != "-":
                        df = df.append({
                            'Date': row['Date'],
                            'Charge': row[f'{reps} répétitions'],
                            'Répétitions': reps
                        }, ignore_index=True)

        return df.sort_values(by='Date', ascending=False)


    ###############################
    def create_specific_dataframe(self, table, exercise_id): # à refaire
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



