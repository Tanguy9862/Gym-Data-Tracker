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