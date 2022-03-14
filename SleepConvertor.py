class ConvertSleepData:

    def conv_time_float(self, value):
        vals = value.split(':')
        t, hours = divmod(float(vals[0]), 24)
        t, minutes = divmod(float(vals[1]), 60)
        minutes = minutes / 60.0
        return hours + minutes

    def float_to_time(self, hours, decimal):
        formatted_decimal = round(float(f'0.{decimal}') * 60, 2)
        if formatted_decimal == 0.0:
            formatted_decimal = str(formatted_decimal).join('00')
        return f'{hours}:{formatted_decimal}'
