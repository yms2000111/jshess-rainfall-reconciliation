"""V5 canonical mathematics shared by Word, LaTeX and the equation guide."""
from v4_equations import EQUATIONS as PREVIOUS
EQUATIONS = dict(PREVIOUS)
EQUATIONS[12] = (
    r'\begin{gathered}'
    r'\widehat g_s=1-\frac{V_{\mathrm{lin},s}}{V_{\mathrm{BU},s}},\\'
    r'V_{\mathrm{lin},s}=[\boldsymbol P\boldsymbol\Omega_s\boldsymbol P^{\mathsf T}]_{77},\qquad '
    r'\boldsymbol P=\boldsymbol S_7\boldsymbol G,\\'
    r'V_{\mathrm{BU},s}=\boldsymbol1_4^{\mathsf T}\boldsymbol\Omega_{s,bb}\boldsymbol1_4.'
    r'\end{gathered}'
)
