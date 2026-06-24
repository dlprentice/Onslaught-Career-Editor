/* address: 0x00444160 */
/* name: CDestroyableSegment__Unk_00444160 */
/* signature: void __fastcall CDestroyableSegment__Unk_00444160(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CDestroyableSegment__Unk_00444160(int param_1)

{
  void *item;
  float fVar1;
  float fVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int *piVar6;
  int unaff_EDI;
  bool bVar7;
  double dVar8;
  undefined4 *local_1c [2];
  undefined4 *local_14;
  void *pvStack_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d2158;
  pvStack_c = ExceptionList;
  ExceptionList = &pvStack_c;
  CSPtrSet__Init(local_1c);
  iVar5 = 0;
  local_4 = 0;
  if (0 < *(int *)(param_1 + 8)) {
    do {
      if (((iVar5 != -1) &&
          (item = *(void **)(*(int *)(param_1 + 4) + iVar5 * 4), item != (void *)0x0)) &&
         (iVar3 = CSPtrSet__Contains(local_1c,item,unaff_EDI), iVar3 == 0)) {
        CSPtrSet__AddToTail(local_1c,item);
      }
      iVar5 = iVar5 + 1;
    } while (iVar5 < *(int *)(param_1 + 8));
  }
  local_14 = local_1c[0];
  if (local_1c[0] == (undefined4 *)0x0) {
    piVar6 = (int *)0x0;
  }
  else {
    piVar6 = (int *)*local_1c[0];
  }
  while (piVar6 != (int *)0x0) {
    iVar5 = (**(code **)(*piVar6 + 0x14))();
    if (1 < iVar5) {
      uVar4 = Random__NextLCGAbs(DAT_008a9d9c);
      uVar4 = uVar4 & 0x80000001;
      bVar7 = uVar4 == 0;
      if ((int)uVar4 < 0) {
        bVar7 = (uVar4 - 1 | 0xfffffffe) == 0xffffffff;
      }
      if (bVar7) {
        (**(code **)(*piVar6 + 0xc))(0x47c35000,*(undefined4 *)(param_1 + 0x10));
      }
    }
    local_14 = (undefined4 *)local_14[1];
    if (local_14 == (undefined4 *)0x0) {
      piVar6 = (int *)0x0;
    }
    else {
      piVar6 = (int *)*local_14;
    }
  }
  if (*(int *)(param_1 + 0x2c) != 1) {
    iVar5 = *(int *)(param_1 + 8);
    bVar7 = true;
    fVar1 = _DAT_005d8568;
    if (0 < iVar5) {
      piVar6 = *(int **)(param_1 + 4);
      do {
        if ((*piVar6 != 0) && (*(int *)(*piVar6 + 0x1c) == 1)) {
          bVar7 = false;
        }
        piVar6 = piVar6 + 1;
        iVar5 = iVar5 + -1;
      } while (iVar5 != 0);
      if (!bVar7) {
        dVar8 = CDestroyableSegment__Helper_00442890(*(void **)(param_1 + 0xc));
        fVar1 = (float)dVar8;
      }
    }
    iVar5 = *(int *)(param_1 + 8);
    bVar7 = true;
    fVar2 = _DAT_005d8568;
    if (0 < iVar5) {
      piVar6 = *(int **)(param_1 + 4);
      do {
        if ((*piVar6 != 0) && (*(int *)(*piVar6 + 0x1c) == 1)) {
          bVar7 = false;
        }
        piVar6 = piVar6 + 1;
        iVar5 = iVar5 + -1;
      } while (iVar5 != 0);
      if (!bVar7) {
        fVar2 = *(float *)(param_1 + 0x18);
      }
    }
    if (fVar1 < fVar2 * _DAT_005d85ec) {
      *(undefined4 *)(param_1 + 0x2c) = 1;
    }
  }
  local_4 = 0xffffffff;
  CSPtrSet__Clear(local_1c);
  ExceptionList = pvStack_c;
  return;
}
