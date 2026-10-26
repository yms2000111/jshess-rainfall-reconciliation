"""Canonical equations shared by the final Word and LaTeX manuscripts."""
EQUATIONS={
1:r'\boldsymbol y_5=\boldsymbol S_5\boldsymbol b,\qquad \boldsymbol y_7=\boldsymbol S_7\boldsymbol b,\qquad \boldsymbol b=(w_1,w_2,w_3,w_4)^{\mathsf T}.',
2:r'\boldsymbol S_7=\left(\begin{matrix}1&0&0&0\\0&1&0&0\\0&0&1&0\\0&0&0&1\\1&1&0&0\\0&0&1&1\\1&1&1&1\end{matrix}\right).',
3:r'Y=\max(Z-\delta,0),\qquad Z\sim\operatorname{Gamma}(\kappa,\theta).',
4:r'\mu=a+b\bar x,\qquad \sigma^2=c+d\bar x+e s_x^2,\qquad \kappa=\mu^2/\sigma^2,\quad \theta=\sigma^2/\mu.',
5:r'\mu_{\mathrm{H1}}=\mu_{\mathrm{H0}}\exp(\boldsymbol\beta^{\mathsf T}\boldsymbol z).',
6:r'\boldsymbol G=(\boldsymbol S^{\mathsf T}\boldsymbol W^{-1}\boldsymbol S)^{-1}\boldsymbol S^{\mathsf T}\boldsymbol W^{-1},\qquad \widetilde{\boldsymbol y}=\boldsymbol S\boldsymbol G\widehat{\boldsymbol y}.',
7:r'\boldsymbol b^*=\underset{\boldsymbol b\geq\boldsymbol0}{\operatorname{argmin}}\;(\boldsymbol S\boldsymbol b-\boldsymbol v)^{\mathsf T}\boldsymbol W^{-1}(\boldsymbol S\boldsymbol b-\boldsymbol v),\qquad \boldsymbol v^*=\boldsymbol S\boldsymbol b^*.',
8:r'\widetilde w_k=\widehat w_k+\frac{\sigma_k^2}{\sigma_m^2+s}\left(\widehat m-\sum\limits_{j=1}^{4}\widehat w_j\right),\qquad s=\sum\limits_{j=1}^{4}\sigma_j^2.',
9:r'\operatorname{CRPS}=\frac1M\sum\limits_{i=1}^{M}{\left|x^{(i)}-y\right|}-\frac1{2M^2}\sum\limits_{i=1}^{M}{\sum\limits_{j=1}^{M}{\left|x^{(i)}-x^{(j)}\right|}}.',
10:r'\operatorname{twCRPS}_{q}=\operatorname{CRPS}\big(\{\max(x^{(i)},q)\}_{i=1}^{M},\max(y,q)\big).',
12:r'\widehat g_s=1-\frac{[\boldsymbol P\boldsymbol\Omega_s\boldsymbol P^{\mathsf T}]_{77}}{\boldsymbol1^{\mathsf T}\boldsymbol\Omega_{s,bb}\boldsymbol1},\qquad \boldsymbol P=\boldsymbol S_7\boldsymbol G.',
14:r'g(T)=s_0\exp(a)\left(T/s_0\right)^{\exp(b)},\qquad T\geq0.',
15:r'\widetilde w_k=\frac{w_k}{T}g(T)\quad(T>0),\qquad \widetilde w_k=0\quad(T=0),\qquad \sum\limits_{k=1}^{4}\widetilde w_k=g(T).'
}
