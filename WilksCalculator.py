
class WilksCalculator:

    def __init__(self):
        pass

    def wilks_calculation(self, sex, bw, total):
        if sex == "Male":
            a = -216.0475144
            b = 16.2606339
            c = -0.002388645
            d = -0.00113732
            e = 7.01863*10**-6
            f = -1.291*10**-8

            return self.wilks_coef(a=a, b=b, c=c, d=d, e=e, f=f, x=bw, total=total)

        else:
            a = 594.31747775582
            b = -27.23842536447
            c = 0.82112226871
            d = -0.00930733913
            e = 4.731582*10**-5
            f = -9.054*10**-8

            return self.wilks_coef(a=a, b=b, c=c, d=d, e=e, f=f, x=bw, total=total)

    def wilks_coef(self, a, b, c, d, e, f, x, total):
        coef = round(total*500/(a + b*x + c*x**2 + d*x**3 + e*x**4 + f*x**5),2)
        return coef