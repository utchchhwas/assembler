add $t0,$zero,$zero
addi $t1,$zero,5
LOOP:
    bneq $t1,$zero,END_LOOP
    add $t0,$t0,$t1
    subi $t1,$t1,1
    j LOOP
END_LOOP: