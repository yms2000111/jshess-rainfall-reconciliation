"""Additional canonical equations, shared by Word and LaTeX."""
from final_equations import EQUATIONS as ORIGINAL
EQUATIONS=dict(ORIGINAL)
EQUATIONS[16]=r'P_t^*=\sum\limits_{j=1}^{3}{w_{j,t}P_{j,t}},\qquad w_{j,t}=\frac{\exp(\boldsymbol\alpha_j^{\mathsf T}\boldsymbol x_t)}{\sum\limits_{k=1}^{3}{\exp(\boldsymbol\alpha_k^{\mathsf T}\boldsymbol x_t)}}.'
EQUATIONS[17]=r'\operatorname{CRPS}(P_t^*,y_t)=\sum\limits_{j=1}^{3}{w_{j,t}A_{j,t}}-\frac12\sum\limits_{j=1}^{3}{\sum\limits_{k=1}^{3}{w_{j,t}w_{k,t}B_{jk,t}}}.'
