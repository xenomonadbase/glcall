glcall
======

global gtags bash completed function name caller callee explorer

confirmed to work on gnu global version 6.2.8

quickly do function caller/callee analysis using gnu global 6.x feature
and let bash completion to list out the next possible caller/callee site
and let human to choose which one is correct

handy for code traversing in command line environment

Install
=======

sudo make install
installs files to /usr/local/bin/. and /etc/bash_completion.d/.

Usage(setup)
============

    $ cd linux
    $ gtags


Usage(completing next calling function)
=======================================


    $ glcall -x start_kern[TAB]
    start_kernel
    
    $ glcall -x start_kernel [TAB]
    Display all 124 possibilities? (y or n)
    DEBUG_ADDRESSES           calibrate_delay           kmemleak_init             rest_init
    DEBUG_LAST_STEPS          call_function_init        local_irq_disable         runkernel
    EFI_RUNTIME_SERVICES      cgroup_init               local_irq_enable          sched_clock_init
    ...

    $ glcall -x start_kernel [RET]
    ...
    start_kernel:471 => cred_init:609         |init/main.c                         |cred_init();
    start_kernel:471 => fork_init:610         |init/main.c                         |fork_init(totalram_pages);
    start_kernel:471 => proc_caches_init:611  |init/main.c                         |proc_caches_init();
    start_kernel:471 => buffer_init:612       |init/main.c                         |buffer_init();
    ...

    $ glcall -x start_kernel setup_arch [TAB]....
    ...
    $ glcall -x start_kernel setup_arch paging_init bootmem_init arm_bootmem_init[RET]
    setup_arch:759 => paging_init:790         |arch/arm/kernel/setup.c             |paging_init(mdesc);
     paging_init:41 => bootmem_init:44         |arch/arm/mm/nommu.c                 |bootmem_init();
      bootmem_init:390 => arm_bootmem_init:398  |arch/arm/mm/init.c                  |arm_bootmem_init(min, max_low);
       arm_bootmem_init:155 => memblock_region:158  |arch/arm/mm/init.c                  |struct memblock_region *reg;
       arm_bootmem_init:155 => reg:158           |arch/arm/mm/init.c                  |struct memblock_region *r
  
 Usage(completing next caller function)
=======================================
    
    $ glcall -r bio_end_flush [TAB]
    ...
    $ glcall -r bio_end_flush blkdev_issue_flush ext4_sync_file ext4_release_dir ext4_release_dir
    bio_end_flush:433 <= blkdev_issue_flush:408  |block/blk-flush.c                   |bio->bi_end_io = bio_end_flush;
     blkdev_issue_flush:171 <= ext4_sync_file:114  |fs/ext4/fsync.c                     |err = blkdev_issue_flush(inode->i_sb->s_bdev, GFP_KERNEL, NULL);
      ext4_sync_file:632 <= ext4_release_dir:616  |fs/ext4/dir.c                       |.fsync      = ext4_sync_file,
       ext4_release_dir:633 <= ext4_release_dir:616  |fs/ext4/dir.c                       |.release = ext4_release_dir,
       ext4_release_dir:633 <= ext4_release_dir:616  |fs/ext4/dir.c                       |.release    = ext4_release_dir,

TODO
====

* use LLVM clang-ctags for more precise analysis of c/c++ code
* or get static analysis information from DWARF not from source code should be better if DWARF is available
* check other languages like haskell javascript python works...
* not only CFG but DFG or CDFG and visualize the traversed call tree in browser in realtime or something...

License
=======
Copyright (c) https://github.com/xenomonadbase/glcall.git
EPL-1.0

