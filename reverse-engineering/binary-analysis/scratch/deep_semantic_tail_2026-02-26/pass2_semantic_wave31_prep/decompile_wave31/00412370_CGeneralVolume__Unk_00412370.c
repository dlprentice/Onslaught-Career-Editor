/* address: 0x00412370 */
/* name: CGeneralVolume__Unk_00412370 */
/* signature: double __fastcall CGeneralVolume__Unk_00412370(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CGeneralVolume__Unk_00412370(void *param_1)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  int *piVar5;
  int local_4;

  piVar5 = *(int **)param_1;
  iVar4 = 0;
  *(int **)((int)param_1 + 8) = piVar5;
  if (piVar5 == (int *)0x0) {
    iVar1 = 0;
  }
  else {
    iVar1 = *piVar5;
  }
  if (iVar1 != 0) {
    do {
      if (iVar4 == *(int *)((int)param_1 + 0x10)) {
        if (iVar1 != 0) {
          iVar4 = 0;
          iVar2 = 0;
          piVar3 = (int *)(*(int *)(iVar1 + 0xa4) + 0xc);
          piVar5 = piVar3;
          do {
            if (*piVar5 != -1) {
              iVar4 = iVar2;
            }
            iVar2 = iVar2 + 100;
            piVar5 = piVar5 + 1;
          } while (iVar2 < 500);
          if (iVar4 != 0) {
            local_4 = 0;
            iVar4 = 0;
            do {
              if (*piVar3 != -1) {
                local_4 = iVar4;
              }
              iVar4 = iVar4 + 100;
              piVar3 = piVar3 + 1;
            } while (iVar4 < 500);
            return (double)(*(float *)(iVar1 + 0x60) / (float)local_4);
          }
          return (double)_DAT_005d856c;
        }
        break;
      }
      iVar4 = iVar4 + 1;
      piVar5 = *(int **)(*(int *)((int)param_1 + 8) + 4);
      *(int **)((int)param_1 + 8) = piVar5;
      if (piVar5 == (int *)0x0) {
        iVar1 = 0;
      }
      else {
        iVar1 = *piVar5;
      }
    } while (iVar1 != 0);
  }
  return (double)_DAT_005d856c;
}
