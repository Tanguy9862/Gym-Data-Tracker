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
                "Notes": exercise_performance.notes if exercise_performance.notes is not None else '-',
                "Sommeil": exercise_performance.sleep_time if exercise_performance.sleep_time is not None else '-'
            }
            df_global_exercise_performance = df_global_exercise_performance.append(new_row, ignore_index=True)

        return df_global_exercise_performance

    def create_global_df(self, all_performances):
        df = pd.DataFrame(columns=['Date', 'Performance globale', 'Notes'])

        for perf in all_performances:
            df = df.append({'Date': perf.date_performance,
                                          'Performance globale': perf.global_performance,
                                          'Notes': perf.notes if perf.notes is not None else '-',
                                          'Sommeil': perf.sleep_time if perf.sleep_time is not None else '-'},
                                         ignore_index=True)

        return df.sort_values(by='Date', ascending=False)

    def create_specific_df(self, highest_reps, all_performances, reps_range):
        """
        :param highest_reps: Highest value of repetition
        :param all_performances: List of all_performances object for an exercise
        :param reps_range: List of min repetitions to max repetitions
        :return: Pandas dataFrame
        """
        df = pd.DataFrame(columns=['Date'])

        for reps in reps_range:
            if reps == 1:
                df[f'{reps} r??p??tition'] = ""
            else:
                df[f'{reps} r??p??titions'] = ""

        for perf in all_performances:

            if perf.repetitions <= highest_reps:
                for reps in reps_range:
                    if reps == perf.repetitions and reps == 1:
                        df = df.append({
                            'Date': perf.date,
                            f'{reps} r??p??tition': perf.weight
                        }, ignore_index=True)
                    elif reps == perf.repetitions and reps != 1:
                        df = df.append({
                            'Date': perf.date,
                            f'{reps} r??p??titions': perf.weight
                        }, ignore_index=True)

        df = df.fillna(0)
        df = df.groupby('Date').max().reset_index().replace(to_replace=0, value='-')

        return df.sort_values(by='Date', ascending=False)

    def add_rpe_to_df(self, df, all_performances, reps_range):
        """
        :param df: Specific dataframe based on create_specific_df method
        :param all_performances: List of all_performances object for an exercise
        :param reps_range: List of min repetitions to max repetitions
        :return: Pandas dataframe which include RPE
        """

        for perf in all_performances:
            if perf.repetitions in reps_range:
                if perf.rpe is not None:
                    if perf.repetitions > 1:
                        df.loc[(df[f'{perf.repetitions} r??p??titions'] == perf.weight) & (df[
                                                                                             'Date'] == perf.date), f'{perf.repetitions} r??p??titions'] = f'{perf.weight}@{perf.rpe}'
                    else:
                        df.loc[(df[f'{perf.repetitions} r??p??tition'] == perf.weight) & (df[
                                                                                            'Date'] == perf.date), f'{perf.repetitions} r??p??tition'] = f'{perf.weight}@{perf.rpe}'

        return df.sort_values(by='Date', ascending=False)

    def create_df_for_plot(self, data_df, reps_range):
        df = pd.DataFrame(columns=['Date', 'Charge', 'R??p??titions'])

        for index, row in data_df.iterrows():
            for reps in reps_range:
                if reps == 1:
                    if row[f'{reps} r??p??tition'] != "-":
                        df = df.append({
                            'Date': row['Date'],
                            'Charge': row[f'{reps} r??p??tition'],
                            'R??p??titions': reps
                        }, ignore_index=True)
                else:
                    if row[f'{reps} r??p??titions'] != "-":
                        df = df.append({
                            'Date': row['Date'],
                            'Charge': row[f'{reps} r??p??titions'],
                            'R??p??titions': reps
                        }, ignore_index=True)

        return df.sort_values(by='Date', ascending=False)

    def create_df_for_edit(self, all_global_performances):
        df_exercise = pd.DataFrame(columns=['Performance_id', 'Date', 'Performance globale', 'Notes', 'Sommeil'])
        for perf in all_global_performances:
            df_exercise = df_exercise.append({
                'Performance_id': perf.id,
                'Date': perf.date_performance,
                'Performance globale': perf.global_performance,
                'Notes': perf.notes if perf.notes is not None else '-',
                'Sommeil': perf.sleep_time if perf.sleep_time is not None else '-'
            }, ignore_index=True)

        df_exercise = df_exercise.sort_values(by='Date', ascending=False)
        df_exercise['Editer'] = "Editer"
        df_exercise['Delete'] = "Supprimer"

        return df_exercise
