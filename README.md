# kbdgen

Optimized keyboard layout generator using simulated annealing 

# Usage

```sh 
usage: kbdgen [-h] [-c CLAMP] [-m MAX_ITER] [-d DECAY] [-e EPOCH] [-f FILE]

Simulated Annealing based keyboard layout generator

options:
  -h, --help            show this help message and exit
  -c CLAMP, --clamp CLAMP
                        number of swaps n; n=clamp(T/clamp_scale, 1, 26)
  -m MAX_ITER, --max-iter MAX_ITER
                        maximum number of iterations
  -d DECAY, --decay DECAY
                        T*=decay
  -e EPOCH, --epoch EPOCH
                        number of iters before T decays
  -f FILE, --file FILE  file to use as example input
```
