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