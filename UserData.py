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

    def get_last_date_last_pr(self, index, table, user_id, df):
        """
        Get the last date of the last PR
        :param index: row in join_df
        :return: most recent date of the last PR
        """

        squat_date = table.query.filter_by(user_id=user_id,
                                               weight=df['Squat'].iloc[index]).first().date
        bench_date = table.query.filter_by(user_id=user_id,
                                               weight=df['Bench'].iloc[index]).first().date
        deadlift_date = table.query.filter_by(user_id=user_id,
                                                  weight=df['Deadlift'].iloc[index]).first().date

        all_dates = [datetime.strptime(f'{squat_date}', '%Y-%m-%d'),
                     datetime.strptime(f'{bench_date}', '%Y-%m-%d'),
                     datetime.strptime(f'{deadlift_date}', '%Y-%m-%d')]

        return max(all_dates)

    def check_format_of_data(self, all_perfs):
        """
        Checking if the data of global performance passed by the user is correctly formatted
        :param all_perfs: List of global performance
        :return: Boolean
        """

        for n in range(len(all_perfs)):
            split_perf = all_perfs[n].split('x')
            if len(split_perf) != 3 and len(split_perf) != 2:
                return False
            else:
                for value in split_perf:
                    if '@' not in value:
                        try:
                            float(value)
                        except ValueError:
                            return False
                    else:
                        new_value = value.split('@')
                        for _ in new_value:
                            try:
                                float(_)
                            except ValueError:
                                return False
        return True

    def check_format_of_rpe(self, all_perfs):
        """
        Checking if the RPE is correctly formatted and in a range of 1 to 10
        :param all_perfs: List of global performance
        :return: Boolean
        """

        for perf in all_perfs:
            if '@' in perf:
                current_rpe = perf.split('@')
                if float(current_rpe[1]) < 1 or float(current_rpe[1]) > 10:
                    return False
        return True

    def check_format_of_sleep_time(self, sleep_time_data):

        try:
            current_sleep = datetime.strptime(f'{sleep_time_data.lower()}', '%H:%M').strftime('%H:%M')
        except ValueError:
            return False
        else:
            return current_sleep





