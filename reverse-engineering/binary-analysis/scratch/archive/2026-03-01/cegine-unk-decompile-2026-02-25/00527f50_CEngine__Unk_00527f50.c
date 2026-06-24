/* address: 0x00527f50 */
/* name: CEngine__Unk_00527f50 */
/* signature: int CEngine__Unk_00527f50(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CEngine__Unk_00527f50(void)

{
  char cVar1;
  DWORD DVar2;
  uint uVar3;
  undefined1 *puVar4;
  undefined4 *puVar5;
  undefined1 *puVar6;
  int iVar7;
  undefined1 *puVar8;
  int *piVar9;
  undefined1 *puVar10;
  int local_28;
  undefined1 local_24 [4];
  undefined1 local_20 [4];
  undefined1 local_1c [8];
  undefined1 *local_14;
  HANDLE local_10;
  HANDLE local_c;
  HANDLE local_8;
  undefined4 local_4;

  local_10 = DAT_0089beb8;
  local_c = DAT_0089bec4;
  local_8 = DAT_0089bec0;
  local_4 = DAT_0089bebc;
  puVar4 = local_14;
switchD_00527fc8_default:
  while( true ) {
    DAT_0089beb0 = 0;
    DVar2 = WaitForMultipleObjects(4,&local_10,0,0xffffffff);
    if (DVar2 != 0xffffffff) break;
    GetLastError();
    Sleep(100);
  }
  DAT_0089bea8 = DVar2;
  DAT_0089beb0 = 1;
  switch(DVar2) {
  case 0:
    (**(code **)(*DAT_0089bfd4 + 0xc))();
    DAT_0089bed0 = 0;
    DAT_0089becc = 0;
    (**(code **)(*DAT_0089bfd4 + 4))(&DAT_0089bed4);
    DAT_0089beac = 0;
    cVar1 = (**(code **)(*DAT_0089bfd4 + 0x10))();
    if (((cVar1 == '\0') || (iVar7 = (**(code **)(*DAT_0089bfd4 + 0x18))(), iVar7 != 2)) ||
       (iVar7 = (**(code **)(*DAT_0089bfd4 + 0x14))(), iVar7 != 0xac44)) {
      if (DAT_0089bec8 != (int *)0x0) {
        (**(code **)(*DAT_0089bec8 + 0x48))(DAT_0089bec8);
        ResetEvent(DAT_0089bec4);
        ResetEvent(DAT_0089bec0);
        ResetEvent(CEngine__Unk_00528540);
      }
      goto switchD_00527fc8_default;
    }
    if ((DAT_0089bec8 != (int *)0x0) &&
       ((**(code **)(*DAT_0089bec8 + 0x24))(DAT_0089bec8,&local_14), ((uint)local_14 & 5) != 0))
    goto switchD_00527fc8_default;
    puVar10 = local_1c;
    piVar9 = &local_28;
    puVar8 = local_24;
    iVar7 = 0;
    puVar6 = (undefined1 *)0x0;
    (**(code **)(*DAT_0089bec8 + 0x2c))(DAT_0089bec8,0,0,puVar8,piVar9,puVar10,local_20,2);
    (**(code **)(*DAT_0089bfd4 + 8))(piVar9,puVar10,&stack0xffffffc8);
    if (puVar10 == (undefined1 *)0x0) {
      DAT_0089beac = 1;
      if (DAT_0089bec8 != (int *)0x0) {
        (**(code **)(*DAT_0089bec8 + 0x48))(DAT_0089bec8);
        ResetEvent(DAT_0089bec4);
        ResetEvent(DAT_0089bec0);
        ResetEvent(CEngine__Unk_00528540);
      }
      (**(code **)(*DAT_0089bec8 + 0x4c))(DAT_0089bec8,iVar7,puVar6,piVar9,puVar8);
      goto switchD_00527fc8_default;
    }
    if (puVar10 < puVar6) {
      puVar5 = (undefined4 *)(puVar10 + iVar7);
      for (uVar3 = (uint)((int)puVar6 - (int)puVar10) >> 2; uVar3 != 0; uVar3 = uVar3 - 1) {
        *puVar5 = 0;
        puVar5 = puVar5 + 1;
      }
      for (uVar3 = (int)puVar6 - (int)puVar10 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
        *(undefined1 *)puVar5 = 0;
        puVar5 = (undefined4 *)((int)puVar5 + 1);
      }
      DAT_0089bed0 = DAT_0089bed0 + 1;
    }
    (**(code **)(*DAT_0089bec8 + 0x4c))(DAT_0089bec8,iVar7,puVar6,piVar9,puVar8);
    (**(code **)(*DAT_0089bec8 + 0x34))(DAT_0089bec8,0);
    (**(code **)(*DAT_0089bec8 + 0x30))(DAT_0089bec8,0,0,1);
    break;
  case 1:
  case 2:
    if (2 < DAT_0089bed0) {
      if (DAT_0089bec8 != (int *)0x0) {
        (**(code **)(*DAT_0089bec8 + 0x48))(DAT_0089bec8);
        ResetEvent(DAT_0089bec4);
        ResetEvent(DAT_0089bec0);
        ResetEvent(CEngine__Unk_00528540);
      }
      (**(code **)(*DAT_0089bfd4 + 0xc))();
      DAT_0089bed0 = 0;
      DAT_0089becc = 0;
      DAT_0089beac = 1;
      goto switchD_00527fc8_default;
    }
    if (DVar2 == 1) {
      puVar4 = (undefined1 *)0x0;
    }
    else if (DVar2 == 2) {
      puVar4 = (undefined1 *)0x40000;
    }
    puVar10 = local_1c;
    piVar9 = &local_28;
    puVar8 = local_24;
    iVar7 = 0x40000;
    puVar6 = puVar4;
    (**(code **)(*DAT_0089bec8 + 0x2c))
              (DAT_0089bec8,puVar4,0x40000,puVar8,piVar9,puVar10,local_20,0);
    (**(code **)(*DAT_0089bfd4 + 8))(piVar9,puVar10,&stack0xffffffc8);
    if (puVar10 < puVar6) {
      puVar5 = (undefined4 *)(puVar10 + iVar7);
      for (uVar3 = (uint)((int)puVar6 - (int)puVar10) >> 2; uVar3 != 0; uVar3 = uVar3 - 1) {
        *puVar5 = 0;
        puVar5 = puVar5 + 1;
      }
      for (uVar3 = (int)puVar6 - (int)puVar10 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
        *(undefined1 *)puVar5 = 0;
        puVar5 = (undefined4 *)((int)puVar5 + 1);
      }
      DAT_0089bed0 = DAT_0089bed0 + 1;
    }
    (**(code **)(*DAT_0089bec8 + 0x4c))(DAT_0089bec8,iVar7,puVar6,piVar9,puVar8);
    break;
  case 3:
    goto switchD_00527fc8_caseD_3;
  default:
    goto switchD_00527fc8_default;
  }
  DAT_0089becc = DAT_0089becc + local_28;
  goto switchD_00527fc8_default;
switchD_00527fc8_caseD_3:
  DAT_0089beb0 = 0;
  return 0;
}
