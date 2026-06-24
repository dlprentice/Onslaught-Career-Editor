/* address: 0x00412480 */
/* name: CGeneralVolume__Unk_00412480 */
/* signature: int __fastcall CGeneralVolume__Unk_00412480(void * param_1) */


int __fastcall CGeneralVolume__Unk_00412480(void *param_1)

{
  int *piVar1;
  int iVar2;
  int iVar3;

  piVar1 = *(int **)param_1;
  iVar3 = 0;
  *(int **)((int)param_1 + 8) = piVar1;
  if (piVar1 == (int *)0x0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *piVar1;
  }
  if (iVar2 != 0) {
    do {
      if (iVar3 == *(int *)((int)param_1 + 0x10)) {
        if (iVar2 == 0) {
          return 0;
        }
        return **(int **)(iVar2 + 0xa4);
      }
      iVar3 = iVar3 + 1;
      piVar1 = *(int **)(*(int *)((int)param_1 + 8) + 4);
      *(int **)((int)param_1 + 8) = piVar1;
      if (piVar1 == (int *)0x0) {
        iVar2 = 0;
      }
      else {
        iVar2 = *piVar1;
      }
    } while (iVar2 != 0);
  }
  return 0;
}
