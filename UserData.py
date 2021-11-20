from datetime import datetime


class GetUserData:

    def __init__(self):
        pass

    def get_last_bw(self, table, user_id):
        body_user = table.query.filter_by(user_id=user_id).all()

        date_model = datetime.strptime('1900-01-01', '%Y-%m-%d')
        last_bw = None

        # Get the last saved weight:
        for wilks in body_user:
            if wilks.bodyweight != None:
                if datetime.strptime(f'{wilks.date}', '%Y-%m-%d') > date_model:
                    last_bw = wilks.bodyweight
                    date_model = datetime.strptime(f'{wilks.date}', '%Y-%m-%d')
        return last_bw

    def get_highest_pr(self, list_pr, lift_id):
        max_lift = 0
        for pr in list_pr:
            if lift_id == 1:
                if pr.max_squat > max_lift:
                    max_lift = pr.max_squat
            elif lift_id == 2:
                if pr.max_bench > max_lift:
                    max_lift = pr.max_bench
            elif lift_id == 3:
                if pr.max_deadlift > max_lift:
                    max_lift = pr.max_deadlift
        return max_lift

    def get_last_date_last_pr(self, index, table, user_id, df):
        """
        Get the last date of the last PR
        :param index: row in join_df
        :return: most recent date of the last PR
        """

        squat_date = table.query.filter_by(user_id=user_id,
                                               max_squat=df['Squat'].iloc[index]).first().date
        bench_date = table.query.filter_by(user_id=user_id,
                                               max_bench=df['Bench'].iloc[index]).first().date
        deadlift_date = table.query.filter_by(user_id=user_id,
                                                  max_deadlift=df['Deadlift'].iloc[index]).first().date

        all_dates = [datetime.strptime(f'{squat_date}', '%Y-%m-%d'),
                     datetime.strptime(f'{bench_date}', '%Y-%m-%d'),
                     datetime.strptime(f'{deadlift_date}', '%Y-%m-%d')]

        return max(all_dates)



