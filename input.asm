addi $t1, $zero, 3
subi $t2, $zero, -2
add $t0, $t1, $t2
sub $t3, $t1, $t2
nor $t4, $t0, $t2
sw $t1, 3($t2)
srl $t2, $t2, 1
beq $t2, $t3, label1
j end
label1:
sll $t3, $t3, 1
lw $t2, 4($t2)
subi $sp, $sp, 1
sw $t1, 0($sp)
subi $sp, $sp, 1
sw $t2, 0($sp)
j label2
label3:
or $t0, $t0, $t2
andi $t2, $t4, 1
ori $t1, $t1, 5
lw $t2, 0($sp)
addi $sp, $sp, 1
and $t1, $t2, $t4
lw $t1, 0($sp)
addi $sp, $sp, 1
j end
label2:
bneq $t0, $t2, label3
end: