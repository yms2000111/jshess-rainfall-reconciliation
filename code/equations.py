"""Single source for both editable Word equations and LaTeX equations."""
EQUATIONS={
1:r'\boldsymbol{y}=(m,w_1,w_2,w_3,w_4)^{\mathsf{T}}=\boldsymbol{S}\boldsymbol{b},\qquad \boldsymbol{b}=(w_1,w_2,w_3,w_4)^{\mathsf{T}}.',
2:r'\boldsymbol{S}=\left(\begin{matrix}1&1&1&1\\1&0&0&0\\0&1&0&0\\0&0&1&0\\0&0&0&1\end{matrix}\right).',
3:r'Y=\max(Z-\delta,0),\qquad Z\sim\operatorname{Gamma}(\kappa,\theta).',
4:r'\mu=a+b\bar{x},\qquad \sigma^2=c+d\bar{x}+e s_x^2,\qquad \kappa=\mu^2/\sigma^2,\quad \theta=\sigma^2/\mu.',
5:r'\boldsymbol{G}^{*}=(\boldsymbol{S}^{\mathsf{T}}\boldsymbol{W}^{-1}\boldsymbol{S})^{-1}\boldsymbol{S}^{\mathsf{T}}\boldsymbol{W}^{-1},\qquad \widetilde{\boldsymbol{y}}=\boldsymbol{S}\boldsymbol{G}^{*}\widehat{\boldsymbol{y}}.',
6:r'\boldsymbol{b}^{*}=\underset{\boldsymbol{b}\geq\boldsymbol{0}}{\operatorname{arg\,min}}\;(\boldsymbol{S}\boldsymbol{b}-\boldsymbol{v})^{\mathsf{T}}\boldsymbol{W}^{-1}(\boldsymbol{S}\boldsymbol{b}-\boldsymbol{v}),\qquad \boldsymbol{v}^{*}=\boldsymbol{S}\boldsymbol{b}^{*}.',
7:r'\widetilde{w}_k=\widehat{w}_k+\frac{\sigma_k^2}{\sigma_m^2+s}\left(\widehat{m}-\sum_{j=1}^{4}\widehat{w}_j\right),\qquad s=\sum_{j=1}^{4}\sigma_j^2.',
8:r'\widetilde{m}=\frac{\sigma_m^2\sum_{j=1}^{4}\widehat{w}_j+s\widehat{m}}{\sigma_m^2+s}.',
9:r'\operatorname{CRPS}=\frac{1}{M}\sum_{i=1}^{M}\left|x^{(i)}-y\right|-\frac{1}{2M^{2}}\sum_{i=1}^{M}\sum_{j=1}^{M}\left|x^{(i)}-x^{(j)}\right|.',
10:r'\widehat g_s=1-\frac{[\boldsymbol P\boldsymbol\Omega_s\boldsymbol P^{\mathsf T}]_{11}}{\boldsymbol 1^{\mathsf T}\boldsymbol\Omega_{s,bb}\boldsymbol 1},\qquad \boldsymbol P=\boldsymbol S\boldsymbol G^{*}.',
11:r'T=\frac{100}{4|L|}\sum_{r=1}^{4}\sum_{\ell\in L}\frac{\overline{C}_{r\ell}^{\mathrm{rec}}-\overline{C}_{r\ell}^{\mathrm{base}}}{\overline{C}_{r\ell}^{\mathrm{clim}}}.'
}
