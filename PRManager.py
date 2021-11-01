import pandas as pd

class ManagerPR:

    def __init__(self):
        pass

    def create_rm_df(self, pr_data, lift_id):
        """

        :param pr_data: A list of a specific exercise mades on Wilks table
        :param lift_id: 1 for Squat, 2 for Bench, 3 for Deadlift
        :return: DataFrame object with columns refers to Date and Charge

        """
        df_pr = pd.DataFrame(columns=['Date', 'Charge'])

        for pr in pr_data:
            if lift_id == 1:
                lift_data = pr.max_squat
            elif lift_id == 2:
                lift_data = pr.max_bench
            elif lift_id == 3:
                lift_data = pr.max_deadlift
            else:
                lift_data = None

            df_pr = df_pr.append({'Date': pr.date,
                                  'Charge': lift_data}, ignore_index=True)

        return df_pr

    def create_rm_df_by_bw(self, pr_data, lift_id):
        """

                :param pr_data: A list of a specific exercise mades on Wilks table
                :param lift_id: 1 for Squat, 2 for Bench, 3 for Deadlift
                :return: DataFrame object with columns refers to Bodyweight and Charge

                """
        df_pr = pd.DataFrame(columns=['BW', 'Charge'])

        for pr in pr_data:
            if lift_id == 1:
                lift_data = pr.max_squat
            elif lift_id == 2:
                lift_data = pr.max_bench
            elif lift_id == 3:
                lift_data = pr.max_deadlift
            else:
                lift_data = None

            df_pr = df_pr.append({'BW': pr.bodyweight,
                                  'Charge': lift_data}, ignore_index=True)

        return df_pr


    def generate_df_with_highest_pr(self, bw_column, exercise_name, lift_list):
        best_pr_by_bw = pd.DataFrame(columns=['BW', exercise_name])
        for bw in pd.unique(bw_column):
            best_pr_by_bw = best_pr_by_bw.append({'BW': bw,
                                                  exercise_name: lift_list[bw_column == bw].max()[1]},
                                                 ignore_index=True)
        return best_pr_by_bw

