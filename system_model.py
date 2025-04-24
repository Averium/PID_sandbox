from sympy import symbols, diff, sin, cos, Eq, simplify
from sympy.physics.vector import ReferenceFrame, dynamicsymbols

R = ReferenceFrame("R")

ex_ = R.x
ey_ = R.y
ez_ = R.z

m, g, k, f = symbols("m, g, k, f")
x = dynamicsymbols("x")

dx = diff(x, "t")
ddx = diff(dx, "t")

f_ = cos(f) * ex_ + sin(f) * ey_
v_ = dx * f_

E = 1/2 * m * v_.magnitude()**2

q = x
dq = dx

DE_Ddq = diff(E, dq)
d_DE_Ddq_dt = diff(DE_Ddq, "t")
DE_Dq = diff(E, q)

k_ = -v_ * k

B_ = diff(v_, dq, R)
F_ = -g * ey_ + k_

Q = F_.dot(B_)

eq_motion = simplify(Eq(d_DE_Ddq_dt - DE_Dq, Q))

print(eq_motion)