# TIDE

This repository contains the experiments of evaluation and case studies discussed in the paper  
* "Towards Practical Interrupt Side Channel Attacks on macOS for Apple Silicon" (ISCA 2026).
  
TIDE is a precise interrupt detection technique that exploits an explicit macOS behavior arising from Apple’s Double Map mitigation. Using TIDE, we further reverse-engineer Apple’s closed-source interrupt delivery mechanism and reveal that, unlike Linux, Apple’s interrupt controller uniformly distributes shared peripheral interrupts across all active cores.

## Tested Setup

### Software dependencies

In order to run the experiments and proof-of-concepts, the following prerequisites need to be fulfilled:

* Linux installation
  * Build tools (gcc, make)
  * Python 3

* Browsers (for website fingerprinting)
  * Safari browser

### Hardware dependencies

Apple MacBook equipped with an Apple Silicon processor ranging from M1 Pro to M5.
 Throughout our experiments, we successfully evaluated our implementations on the following environments. 
| Machine                | CPU                  | Kernel          |
| ---------------------- | -------------------  | --------------- |
| MacBook Pro 2021       | M1 Pro  | macOS Ventura 13.6    |
| Mac mini 2023   | M2   | macOS Ventura 13.7     |
| MacBook Air 2023   |  M3  | macOS Sonoma 14.6    |
| MacBook Pro 2023 |  M3    | macOS Sonoma 14.7    |
| Mac mini 2020 (Cloud)  |  M1 Max  | macOS Sonoma 14.6    |
| Mac mini 2024 (Cloud)  | M4    | macOS Sequoia 15.2    |

Running the full fingerprinting experiment over 100 websites requires access to a GPU server. To eliminate this requirement, we also provide a simplified version of the experiment.

## Materials

This repository contains the following materials:

* `E1-interrupt-detection`: contains the code that we exploit x18 register to detect interrupts without architectural timers.
* `E2-reverse-engineering`: contains the code that we use TIDE to reverse-engineer the Apple interrupt controller.
* `E3-website-fingerprinting`: contains the code that we apply TIDE for inferring victim website visits.

## Contact

If there are questions regarding these experiments, please send an email to `zhangxin00@stu.pku.edu.cn`.

## How should I cite this work?

Please use the following BibTeX entry:

```latex
@inproceedings{zhang2026tide,
  year={2026},
  title={Towards Practical Interrupt Side Channel Attacks on macOS for Apple Silicon},
  booktitle={International Symposium on Computer Architecture},
  author={Xin Zhang and Chang Liu and Jiajun Zou and Yi Yang and Qingni Shen and Zhi Zhang and Trevor E. Carlson}
}
