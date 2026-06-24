/* address: 0x00574020 */
/* name: CFastVB__RBTreeRotateLeft_00574020 */
/* signature: void __thiscall CFastVB__RBTreeRotateLeft_00574020(void * this, int param_1, int param_2) */


void __thiscall CFastVB__RBTreeRotateLeft_00574020(void *this,int param_1,int param_2)

{
  int *piVar1;
  int *piVar2;

  piVar1 = *(int **)(param_1 + 8);
  *(int *)(param_1 + 8) = *piVar1;
  if (*piVar1 != DAT_009d0c44) {
    *(int *)(*piVar1 + 4) = param_1;
  }
  piVar1[1] = *(int *)(param_1 + 4);
  if (param_1 == *(int *)(*(int *)((int)this + 4) + 4)) {
    *(int **)(*(int *)((int)this + 4) + 4) = piVar1;
    *piVar1 = param_1;
    *(int **)(param_1 + 4) = piVar1;
    return;
  }
  piVar2 = *(int **)(param_1 + 4);
  if (param_1 == *piVar2) {
    *piVar2 = (int)piVar1;
    *piVar1 = param_1;
    *(int **)(param_1 + 4) = piVar1;
    return;
  }
  piVar2[2] = (int)piVar1;
  *piVar1 = param_1;
  *(int **)(param_1 + 4) = piVar1;
  return;
}
