/* address: 0x00574120 */
/* name: CTexture__TreeIteratorNext */
/* signature: void __fastcall CTexture__TreeIteratorNext(void * param_1) */


void __fastcall CTexture__TreeIteratorNext(void *param_1)

{
  int iVar1;
  int iVar2;
  int *piVar3;

  piVar3 = *(int **)param_1;
  if ((piVar3[4] == 0) && (*(int **)(piVar3[1] + 4) == piVar3)) {
    *(int *)param_1 = piVar3[2];
    return;
  }
  iVar1 = *piVar3;
  if (iVar1 == DAT_009d0c44) {
    piVar3 = (int *)piVar3[1];
    if (*(int *)param_1 == *piVar3) {
      do {
        *(int **)param_1 = piVar3;
        piVar3 = (int *)piVar3[1];
      } while (*(int *)param_1 == *piVar3);
    }
    *(int **)param_1 = piVar3;
    return;
  }
  for (iVar2 = *(int *)(iVar1 + 8); iVar2 != DAT_009d0c44; iVar2 = *(int *)(iVar2 + 8)) {
    iVar1 = iVar2;
  }
  *(int *)param_1 = iVar1;
  return;
}
