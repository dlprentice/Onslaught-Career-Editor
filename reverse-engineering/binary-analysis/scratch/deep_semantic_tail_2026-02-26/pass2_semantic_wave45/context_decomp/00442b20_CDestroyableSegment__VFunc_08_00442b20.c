/* address: 0x00442b20 */
/* name: CDestroyableSegment__VFunc_08_00442b20 */
/* signature: void __fastcall CDestroyableSegment__VFunc_08_00442b20(void * param_1) */


void __fastcall CDestroyableSegment__VFunc_08_00442b20(void *param_1)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  int iVar5;
  bool bVar6;
  int iVar7;
  int iVar8;
  void *pvVar9;
  int iVar10;
  int iVar11;
  void *unaff_EDI;
  int iVar12;
  int iStack_34;
  int *apiStack_1c [2];
  int *piStack_14;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 uStack_4;

  uStack_4 = 0xffffffff;
  puStack_8 = &LAB_005d20d8;
  local_c = ExceptionList;
  iVar11 = 0;
  ExceptionList = &local_c;
  *(undefined4 *)((int)param_1 + 0x38) = 1;
  *(undefined4 *)((int)param_1 + 0xc) = 0;
  **(undefined4 **)((int)param_1 + 0x3c) = 1;
  piVar1 = *(int **)(*(int *)(*(int *)((int)param_1 + 0x3c) + 0x10) + 0x30);
  if ((piVar1 != (int *)0x0) && (iVar7 = (**(code **)(*piVar1 + 0x24))(), iVar7 != 0)) {
    iVar2 = *(int *)(*(int *)(iVar7 + 0x160) + *(int *)((int)param_1 + 8) * 4);
    iVar3 = *(int *)(iVar2 + 0x90);
    if (0 < iVar3) {
      do {
        iVar8 = (**(code **)(*piVar1 + 0x4c))(*(undefined4 *)(*(int *)(iVar2 + 0x94) + iVar11 * 4));
        if ((iVar8 != -1) &&
           (pvVar9 = (void *)(**(code **)(*piVar1 + 0x5c))(iVar8), pvVar9 != (void *)0x0)) {
          CUnit__Helper_004cb0b0(pvVar9,0,(int)unaff_EDI);
        }
        iVar11 = iVar11 + 1;
      } while (iVar11 < iVar3);
    }
    iVar11 = *(int *)(*(int *)((int)param_1 + 0x3c) + 0x10);
    CSPtrSet__Init(apiStack_1c);
    puVar4 = *(undefined4 **)(iVar11 + 0x18c);
    uStack_4 = 0;
    if (puVar4 == (undefined4 *)0x0) {
      pvVar9 = (void *)0x0;
    }
    else {
      pvVar9 = (void *)*puVar4;
    }
    while (pvVar9 != (void *)0x0) {
      bVar6 = false;
      iStack_34 = 0;
      if (0 < iVar3) {
        do {
          iVar8 = 0;
          iVar11 = *(int *)(*(int *)(iVar2 + 0x94) + iStack_34 * 4);
          if (0 < *(int *)(iVar7 + 0x1c)) {
            iVar12 = 0;
            do {
              iVar10 = *(int *)(iVar7 + 0x20) + iVar12;
              if ((((!bVar6) && (iVar10 != 0)) && (*(int *)(iVar10 + 0x40) == iVar11)) &&
                 (iVar5 = *(int *)((int)pvVar9 + 1000),
                 iVar10 = CWorldPhysicsManager__MapGunOrSpawnerTagToIndex((void *)(iVar10 + 0x4c)),
                 iVar10 == iVar5)) {
                CSPtrSet__AddToHead(apiStack_1c,pvVar9);
                bVar6 = true;
              }
              iVar8 = iVar8 + 1;
              iVar12 = iVar12 + 0x150;
            } while (iVar8 < *(int *)(iVar7 + 0x1c));
          }
          iStack_34 = iStack_34 + 1;
        } while (iStack_34 < iVar3);
      }
      puVar4 = (undefined4 *)puVar4[1];
      if (puVar4 == (undefined4 *)0x0) {
        pvVar9 = (void *)0x0;
      }
      else {
        pvVar9 = (void *)*puVar4;
      }
    }
    piStack_14 = apiStack_1c[0];
    if (apiStack_1c[0] == (int *)0x0) {
      iVar11 = 0;
    }
    else {
      iVar11 = *apiStack_1c[0];
    }
    while (iVar11 != 0) {
      CDestroyableSegment__Helper_004f9a60
                (*(void **)(*(int *)((int)param_1 + 0x3c) + 0x10),iVar11,unaff_EDI);
      piStack_14 = (int *)piStack_14[1];
      if (piStack_14 == (int *)0x0) {
        iVar11 = 0;
      }
      else {
        iVar11 = *piStack_14;
      }
    }
    CDestructableSegment__Unk_004429a0(param_1);
    uStack_4 = 0xffffffff;
    CSPtrSet__Clear(apiStack_1c);
  }
  ExceptionList = local_c;
  return;
}
