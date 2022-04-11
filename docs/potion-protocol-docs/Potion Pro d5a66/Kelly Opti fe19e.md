# Kelly Optimal Bonding Curves

**A pricing heuristic for risk applications based on Kelly Criterion**

### **Problem Statement**

Consider a systematic seller of insurance contracts. For a given insurance contract, is there a premium heuristic for the seller that on average leads to long term capital growth?

---

### **Proposed solution**

Consider an LP who contributes an initial amount $*C_0$*  into a pool of capital and starts systematically selling insurance, achieving a certain random growth rate $g_i$ at each insurance expiration cycle. 

Nth capital state $*C_N$*  can be expressed as:

$$
\begin{align*}
C_N = C_0 \cdot (1 + g_1) \cdot (1+g_2)\cdot...\cdot(1+g_N)
\tag{1.1}
\end{align*}
$$

Where $g_i$  are growth samples from growth rate function $G$:

$$
\begin{align*}
G(u,p) = \text{Payoff}\Big(S, R, p(u)\Big) \cdot u
\tag{1.2}

\end{align*}
$$

Where $u$ is the utilization rate of capital $u\in[0,1]$ at each cycle,  $p(u)$ is the premium charged as function of $u$, and  $\text{Payoff}$  is a financial gain/loss function of the insurance contract at expiry: 

$$
\begin{align*}

\text{Payoff}\Big(S,R,p(u)\Big)= \begin{cases}
    R-S+p(u) & \text{if  $R<S$}\\
    p(u) & \text{if $R \geq S$}
  \end{cases}
\tag{1.3}
\end{align*}
$$

Where $S$ is the insurance strike price as percentage of current price , $R$ is the random return of the underlying asset being insured, and $p(u)$ is the premium charged by the LP as a function of utilization.

Nth capital (1.1) can be rewritten in exponential form as:

$$
\begin{align*}
C_N = C_0 \cdot \exp\bigg( \sum_{i=0}^{i=N}\ln(1+g_i) \bigg)
\tag{1.4}

\end{align*}
$$

Per law of large numbers as N tends to infinity the sum of samples over N converges to the expected mean:

$$
\mathbb{E}\bigg[\ln\Big(1+G(u,p)\Big)\bigg]
\tag{1.5} = \lim\limits_{N\rightarrow\infty}\sum_{i=0}^{i=N} \frac{\ln(1+g_i)}{N}  
$$

The **Kelly Criterion** is based on finding an optimal allocation fraction $u_{K}$ such that it maximizes (1.5) and therefore (1.1). In typical TradFi applications, $p$ is fixed and $u$ is the only variable in $G$ for which maximization is performed:

$$
\begin{align*}
u_{K} = 

\underset{u}{\arg\max}\bigg(\mathbb{E}\Big[\ln\big(1+G(u,p)\big)\Big]\bigg)
\quad u \in [0,1]

\tag{1.6}

\end{align*}
$$

In the context of DeFi Automatic Market Maker (AMM) insurance selling, utilization is a result of buyer’s demand and not a choice of the seller. Assuming $u_{\text{new}}$ as an input resulting from a new order, an optimal premium $p^*(u)$ can be chosen such that it falls within the solution space of (1.6).

These **Kelly optimal premium** points can be located along the growth rate curve where the derivative with respect to util is 0 (local maximas along util range):

$$
\begin{align*}
\begin{align*}

\frac{\partial \mathbb{E}[ln(1+G(u,p))]}{\partial u}\Bigg|_{{u}_k,{p}}  

=0

  
\end{align*}
\tag{1.7}

\end{align*}
$$

Solving for all all $u_k,p_k$ pairs that meet (1.7), **Kelly Optimal premium curve $p^*(u)$** is found:

$$
\gamma(u,p) = \mathbb E \big[ \ln\big(1+G(u,p)\big) \big]
\\
\\
p^*(u)=\left\{ (u_k,p_k) \quad \text{s.t.} \quad \left.\frac{\partial\gamma(u,p_k)}{\partial u}\right|_{u_k} = 0, \quad u_k,p_k \in [0,1] \right\} \tag{1.8}
$$

Which is equivalent to finding $p^*(u)$ such that for each new possible $u_k$ it complies with:

$$
\gamma(u,p) =  \mathbb E \big[ \ln\big(1+Payoff(S,r,p)\cdot u \big) \big]
\\
\quad \left.\frac{\partial\gamma(u,p^*_k)}{\partial u}\right|_{u_k} =
\sum_{r_{min}}^{r_{max}}Prob(r)\cdot \frac{Payoff(S,r, p^*_k)}{1+Payoff(S,r, p^*_k)\cdot u_k} 
 = 0
\tag{1.9}
$$

**Kelly optimal premium curve** $p^*(u)$ from (1.9) is shown below in white for 100% price insurance on Ethereum 1 day duration:

![Each color line represents the expected growth rate for an LP selling insurance when using a particular premium k. White emergent line is the Kelly Optimal premium curve connecting all derivative = 0 points.](Kelly%20Opti%20fe19e/Untitled.png)

Each color line represents the expected growth rate for an LP selling insurance when using a particular premium k. White emergent line is the Kelly Optimal premium curve connecting all derivative = 0 points.

A section of the growth_rate surface is shown below, with optimal bonding curve $p^*(u)$ highlighted in blue:

![Each dot represents the expected growth rate for an LP selling insurance when using a particular premium k at a certain utilization k. Blue line is the Kelly Optimal premium curve connecting all premium_util combinations where derivative respect to util = 0.](Kelly%20Opti%20fe19e/infinite_garden555.gif)

Each dot represents the expected growth rate for an LP selling insurance when using a particular premium k at a certain utilization k. Blue line is the Kelly Optimal premium curve connecting all premium_util combinations where derivative respect to util = 0.

### Curve **Fitting**

The Kelly Optimal Premium curve $p^*(u)$ fits closely the family of functions:

$$
\begin{align*}
\begin{align*}
p^{*}_{K}(u) \approx 
p^{*'}_{K}(u) =

a\cdot u\cdot \cosh(b\cdot u^c) + d 

  
\end{align*}
\tag{1.9}

\end{align*}
$$

![Untitled](Kelly%20Opti%20fe19e/Untitled%201.png)

### P**erformance backtest**

Results show positive long term growth across all assets as expected from Kelly G constraints:

![Untitled](Kelly%20Opti%20fe19e/Untitled%202.png)

### R**isk/reward pattern (Kelly Optimal)**

Performance spectrum for various risk estimation errors:

![95% Confidence Intervals of LP capital simulations for 3 train_test scenarios after 365 trials::
Yellow=information match;    Green=risk overestimation    Red=risk underestimation](Kelly%20Opti%20fe19e/Untitled%203.png)

95% Confidence Intervals of LP capital simulations for 3 train_test scenarios after 365 trials::
Yellow=information match;    Green=risk overestimation    Red=risk underestimation

### R**isk/reward pattern (Kelly Fractional)**

When applying corrections over Optimal curves, LPs can effectively design their own risk reward response.

![LP capital simulations for 3 train_test scenarios @ 95% Confidence Intervals::   Yellow=overestimate from 10%;    Green=overestimate from 0% Red=overestimate from 50%.](Kelly%20Opti%20fe19e/Untitled%204.png)

LP capital simulations for 3 train_test scenarios @ 95% Confidence Intervals::   Yellow=overestimate from 10%;    Green=overestimate from 0% Red=overestimate from 50%.

### Benchmark Black-Scholes

![Untitled](Kelly%20Opti%20fe19e/Untitled%205.png)

### **Summary**

- Kelly Criterion is used to create optimal premium curves as function of utilization
- Optimal Premiums observed to follow u·cosh(u) function with 4 parameters
- Simulations match analytical expectations = long term average positive capital growth
- Risk response can be enhanced by fractionalizing Kelly
- Kelly premiums better risk adjusted than Black-Scholes for many crypto assets
- Displayed here as insurance but extensible to other risk applications (call options, spreads, coin tosses, etc)

### Further reading

Interactive simulator:

[Streamlit](https://kelly.finance/)

- Jupyter Notebooks
- Github source_code