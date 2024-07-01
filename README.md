# PyIndiaFactorInvesting

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/rraju26/pyIndiaFactorInvesting/main?urlpath=lab)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rraju26/pyIndiaFactorInvesting/blob/main/factor_based_analysis.ipynb)

A Python-based resource for learning about factor investing concepts in the Indian market using Jupyter Notebooks.

## Directory Structure

- `factor_based_analysis.ipynb`: Jupyter Notebook for the analysis.
- `data/`: Directory containing the sample data file.
  - `fba_sample_data.csv`: Sample data file used in the notebook.

## How to Use

Click the Binder badge above to launch the notebook in your browser without any installation. The notebook will try to read the sample data file from the local `data` directory. If it is not available locally, it will fetch the file from the GitHub repository.

Alternatively, click the Google Colab badge to open the notebook in Google Colab. The notebook will automatically fetch the data file from the GitHub repository if it is not available locally.

## Instructions

1. **Clone this repository**:
   ```bash
   git clone https://github.com/rraju26/pyIndiaFactorInvesting.git
   cd pyIndiaFactorInvesting

2. **Install the Required Libraries**:
    ```bash
    pip install -r requirements.txt


3. **Open the Jupyter Notebook**:
    ```bash 
    jupyter notebook factor_based_analysis.ipynb

## About

This project aims to provide a basic guide and tools for performing factor investing analysis in the Indian financial market. It leverages the power of Python and Jupyter Notebooks to make factor-based financial analysis accessible and interactive.

# References
1. Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics, 33*(1), 3-56.
2. Carhart, M. M. (1997). On persistence in mutual fund performance. *The Journal of Finance, 52*(1), 57-82.
3. Fama, E. F., & French, K. R. (2015). A five-factor asset pricing model. *Journal of Financial Economics, 116*(1), 1-22.
4. Raju, R. (2022). Four and Five-Factor Models in the Indian Equities Market. *SSRN eLibrary*, March, 37
5. Raju, R. (2022), A Five-Factor Asset Pricing Model: Preliminary Evidence from India, *SSRN eLibrary*, August, 33
6. Data sourced from [Invespar Data Library: Data Library: Fama-French Factors, Momentum, and Low-Risk Factors for the Indian Market](http://invespar.com/research).