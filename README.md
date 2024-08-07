# PyIndiaFactorInvesting

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/rraju26/pyIndiaFactorInvesting/main?urlpath=lab)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rraju26/pyIndiaFactorInvesting/blob/main/notebooks/factor_based_analysis.ipynb)

A Python-based resource for learning about factor investing concepts in the Indian market using Jupyter Notebooks.

## Directory Structure

- `notebooks/`: Directory containing Jupyter Notebooks.
    - `intro_to_ap.ipynb`: Introduction to Asset Pricing Models.
    - `intro_multicoll.ipynb`: Multicollinearity in Asset Pricing Models Using Indian Data: A Primer
    - `factor_based_analysis.ipynb`: Factor-based Analysis.
 
- `data/`: Directory containing the sample data files.
  - `fba_sample_data.csv`: Sample strategy data file used in the notebooks.
  - `nifty_indices_rets_example.csv`: Monthly returns for some popular indices.

## Prerequisites

Ensure you have Python and Jupyter installed. If not, you can install them using Anaconda or pip.

## How to Use

Click the Binder badge above to launch the notebooks in your browser without any installation. The notebooks will try to read the sample data files from the local `data` directory. If they are not available locally, the files will be fetched from the GitHub repository.

Alternatively, click the Google Colab badge to open the notebooks in Google Colab. The notebooks will automatically fetch the data files from the GitHub repository if they are not available locally.

## Instructions (for local usage)

If you prefer to run the notebooks locally, follow these steps:

1. **Clone this repository**:
   ```bash
   git clone https://github.com/rraju26/pyIndiaFactorInvesting.git
   cd pyIndiaFactorInvesting

2. **Install the Required Libraries**:
    ```bash
    pip install -r requirements.txt

3. **Open the Jupyter Notebooks**:
    ```bash
    jupyter notebook notebooks/intro_to_ap.ipynb
    jupyter notebook notebooks/intro_multicoll.ipynb
    jupyter notebook notebooks/factor_based_analysis.ipynb


## Notebooks
1. **[Introduction to Asset Pricing](notebooks/intro_to_ap.ipynb)**: This notebook introduces key concepts in asset pricing and their applications in the Indian market.
2. **[Multicollinearity in Asset Pricing Models Using Indian Data: A Primer](notebooks/intro_multicoll.ipynb)**: This notebook explores the identification and mitigation of multicollinearity in asset pricing models using Indian financial data.
2. **[Factor-Based Analysis](notebooks/factor_based_analysis.ipynb)**: This notebook covers the basics of factor based analysis and provides practical analysis examples.


## Future Updates

More notebooks will be added to cover additional topics. Suggestions welcome. 

## About

This project aims to provide a basic guide and tools for performing factor investing analysis in the Indian financial market. It leverages the power of Python and Jupyter Notebooks to make factor-based financial analysis accessible and interactive.

# References
1. Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics, 33*(1), 3-56.
2. Carhart, M. M. (1997). On persistence in mutual fund performance. *The Journal of Finance, 52*(1), 57-82.
3. Fama, E. F., & French, K. R. (2015). A five-factor asset pricing model. *Journal of Financial Economics, 116*(1), 1-22.
4. Raju, R. (2022). Four and Five-Factor Models in the Indian Equities Market. *SSRN eLibrary*, March, 37
5. Raju, R. (2022), A Five-Factor Asset Pricing Model: Preliminary Evidence from India, *SSRN eLibrary*, August, 33
6. Data sourced from [Invespar Data Library: Data Library: Fama-French Factors, Momentum, and Low-Risk Factors for the Indian Market](http://invespar.com/research).