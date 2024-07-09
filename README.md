# MARTSIA-demo

## Wiki
Check out the [Wiki](https://github.com/apwbs/MARTSIA-demo/wiki) for a detailed documentation and step-by-step tutorial to run the system.

### This repository
In this repository you find several folders necessary to run the sistem. 
1. In the *blockchain* folder, you find all the necessary data to connect to the blockchain. For example, the smart contract code in the *contracts* folder, the JavaScript code to deploy on-chain the smart contract in the *migrations* folder, and finally the *truffle-config.js* file to connect to the blockchain via truffle.
2. In the *databases* folder, you find the sql files to build the auxiliary relational tables we use in this prototypical implementation of our system to store temporary data (yellow pages, seeds, RSA private keys, etc.).
3. The *input_files* folder is the folder where the input files to be encrypted are stored. You can use whatever folder you desire.

### Literature and links
For more information on MARTSIA, please consult our paper entitled "[MARTSIA: Enabling Data Confidentiality for Blockchain-based Process Execution](https://arxiv.org/abs/2303.17977)" (DOI: [10.1007/978-3-031-46587-1_4](https://doi.org/10.1007/978-3-031-46587-1_4); slides are available on [SlideShare](https://www.slideshare.net/slideshow/martsia-enabling-data-confidentiality-for-blockchainbased-process-execution/263105804)).

If you want a more complete version of MARTSIA, please check our paper entitled "[Enabling Data Confidentiality with Public Blockchains](https://arxiv.org/abs/2308.03791)", submitted to [ACM TOIT(https://dl.acm.org/journal/toit) and currently under review.

### MARTSIA MAIN PAGE
If you want to go back to the main [MARTSIA page please click here](https://github.com/apwbs/MARTSIA).
