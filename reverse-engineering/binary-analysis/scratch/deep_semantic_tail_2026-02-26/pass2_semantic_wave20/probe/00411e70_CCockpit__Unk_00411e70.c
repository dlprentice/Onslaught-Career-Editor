/* address: 0x00411e70 */
/* name: CCockpit__Unk_00411e70 */
/* signature: void __fastcall CCockpit__Unk_00411e70(void * param_1) */


void __fastcall CCockpit__Unk_00411e70(void *param_1)

{
  undefined4 *puVar1;
  int *piVar2;
  int iVar3;
  void *pvVar4;
  int iVar5;
  int iVar6;
  int local_8;

  iVar5 = 0;
  pvVar4 = CSPtrSet__First(param_1);
  if (pvVar4 != (void *)0x0) {
    do {
      if (iVar5 == *(int *)((int)param_1 + 0x10)) goto LAB_00411ea4;
      iVar5 = iVar5 + 1;
      puVar1 = *(undefined4 **)(*(int *)((int)param_1 + 8) + 4);
      *(undefined4 **)((int)param_1 + 8) = puVar1;
      if (puVar1 == (undefined4 *)0x0) {
        pvVar4 = (void *)0x0;
      }
      else {
        pvVar4 = (void *)*puVar1;
      }
    } while (pvVar4 != (void *)0x0);
  }
  pvVar4 = (void *)0x0;
LAB_00411ea4:
  piVar2 = *(int **)param_1;
  iVar3 = *(int *)(*(int *)((int)pvVar4 + 0xa4) + 0x34);
  iVar5 = *(int *)((int)param_1 + 0x10) + 1;
  local_8 = 0;
  *(int **)((int)param_1 + 8) = piVar2;
  if (piVar2 != (int *)0x0) {
    iVar6 = *piVar2;
    local_8 = 0;
    while (iVar6 != 0) {
      local_8 = local_8 + 1;
      piVar2 = *(int **)(*(int *)((int)param_1 + 8) + 4);
      *(int **)((int)param_1 + 8) = piVar2;
      if (piVar2 == (int *)0x0) break;
      iVar6 = *piVar2;
    }
  }
  if (iVar5 == *(int *)((int)param_1 + 0x10)) {
    return;
  }
  do {
    iVar6 = 0;
    pvVar4 = CSPtrSet__First(param_1);
    while (pvVar4 != (void *)0x0) {
      if (iVar6 == iVar5) {
        if (pvVar4 != (void *)0x0) {
          iVar6 = *(int *)(*(int *)((int)pvVar4 + 0xa4) + 0x24);
          if ((*(int *)((int)pvVar4 + 0x9c) != 0) &&
             ((*(int *)(*(int *)((int)param_1 + 0x18) + 0x55c + iVar6 * 4) != 0 ||
              (*(float *)(*(int *)((int)pvVar4 + 0xa4) + 0x20) <=
               *(float *)(*(int *)((int)param_1 + 0x18) + 0x52c + iVar6 * 4))))) {
            *(int *)((int)param_1 + 0x10) = iVar5;
            iVar5 = 0;
            *(undefined4 *)(*(int *)((int)param_1 + 0x18) + 0x588) = 0;
            pvVar4 = CSPtrSet__First(param_1);
            goto joined_r0x00411f7d;
          }
        }
        break;
      }
      iVar6 = iVar6 + 1;
      piVar2 = *(int **)(*(int *)((int)param_1 + 8) + 4);
      *(int **)((int)param_1 + 8) = piVar2;
      if (piVar2 == (int *)0x0) {
        pvVar4 = (void *)0x0;
      }
      else {
        pvVar4 = (void *)*piVar2;
      }
    }
    iVar5 = iVar5 + 1;
    if (local_8 <= iVar5) {
      iVar5 = 0;
    }
    if (iVar5 == *(int *)((int)param_1 + 0x10)) {
      return;
    }
  } while( true );
joined_r0x00411f7d:
  if (pvVar4 == (void *)0x0) goto LAB_00411f9d;
  if (iVar5 == *(int *)((int)param_1 + 0x10)) {
    if (pvVar4 != (void *)0x0) {
      *(undefined4 *)((int)pvVar4 + 0x60) = 0;
    }
    goto LAB_00411f9d;
  }
  iVar5 = iVar5 + 1;
  pvVar4 = CSPtrSet__Next(param_1);
  goto joined_r0x00411f7d;
LAB_00411f9d:
  piVar2 = *(int **)param_1;
  iVar5 = 0;
  *(int **)((int)param_1 + 8) = piVar2;
  if (piVar2 == (int *)0x0) {
    iVar6 = 0;
  }
  else {
    iVar6 = *piVar2;
  }
  if (iVar6 != 0) {
    do {
      if (iVar5 == *(int *)((int)param_1 + 0x10)) goto LAB_00411fd3;
      iVar5 = iVar5 + 1;
      piVar2 = *(int **)(*(int *)((int)param_1 + 8) + 4);
      *(int **)((int)param_1 + 8) = piVar2;
      if (piVar2 == (int *)0x0) {
        iVar6 = 0;
      }
      else {
        iVar6 = *piVar2;
      }
    } while (iVar6 != 0);
  }
  iVar6 = 0;
LAB_00411fd3:
  if (iVar3 != *(int *)(*(int *)(iVar6 + 0xa4) + 0x34)) {
    CGeneralVolume__Unk_00409e80(*(int *)((int)param_1 + 0x18));
  }
  return;
}
