/* address: 0x0056d2e7 */
/* name: CRT__RaiseSignal */
/* signature: int __cdecl CRT__RaiseSignal(int param_1) */


int __cdecl CRT__RaiseSignal(int param_1)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  code *pcVar6;
  undefined4 *puVar7;
  undefined4 local_10;
  undefined4 local_c;

  bVar1 = false;
  if (param_1 == 2) {
    puVar7 = &DAT_009d0c08;
    pcVar6 = DAT_009d0c08;
LAB_0056d36d:
    bVar1 = true;
    CRT__LockByIndex(1);
    iVar2 = param_1;
  }
  else {
    if (((param_1 != 4) && (param_1 != 8)) && (param_1 != 0xb)) {
      if (param_1 == 0xf) {
        puVar7 = &DAT_009d0c14;
        pcVar6 = DAT_009d0c14;
      }
      else if (param_1 == 0x15) {
        puVar7 = &DAT_009d0c0c;
        pcVar6 = DAT_009d0c0c;
      }
      else {
        if (param_1 != 0x16) {
          return -1;
        }
        puVar7 = &DAT_009d0c10;
        pcVar6 = DAT_009d0c10;
      }
      goto LAB_0056d36d;
    }
    iVar2 = CTexture__Helper_00560b93();
    uVar3 = CRT__FindSignalActionEntry(param_1,*(uint *)(iVar2 + 0x50));
    puVar7 = (undefined4 *)(uVar3 + 8);
    pcVar6 = (code *)*puVar7;
  }
  if (pcVar6 == (code *)0x1) {
    if (!bVar1) {
      return 0;
    }
    CTexture__Helper_005611da(1);
    return 0;
  }
  if (pcVar6 == (code *)0x0) {
    if (bVar1) {
      CTexture__Helper_005611da(1);
    }
                    /* WARNING: Subroutine does not return */
    __exit(3);
  }
  if (((param_1 == 8) || (param_1 == 0xb)) || (param_1 == 4)) {
    local_c = *(undefined4 *)(iVar2 + 0x54);
    *(undefined4 *)(iVar2 + 0x54) = 0;
    if (param_1 == 8) {
      local_10 = *(undefined4 *)(iVar2 + 0x58);
      *(undefined4 *)(iVar2 + 0x58) = 0x8c;
      goto LAB_0056d3e1;
    }
  }
  else {
LAB_0056d3e1:
    if (param_1 == 8) {
      if (DAT_00656120 < DAT_00656124 + DAT_00656120) {
        iVar4 = DAT_00656120 * 0xc;
        iVar5 = DAT_00656120;
        do {
          iVar4 = iVar4 + 0xc;
          *(undefined4 *)(*(int *)(iVar2 + 0x50) + -4 + iVar4) = 0;
          iVar5 = iVar5 + 1;
        } while (iVar5 < DAT_00656124 + DAT_00656120);
      }
      goto LAB_0056d41f;
    }
  }
  *puVar7 = 0;
LAB_0056d41f:
  if (bVar1) {
    CTexture__Helper_005611da(1);
  }
  if (param_1 == 8) {
    (*pcVar6)(8,*(undefined4 *)(iVar2 + 0x58));
  }
  else {
    (*pcVar6)(param_1);
    if ((param_1 != 0xb) && (param_1 != 4)) {
      return 0;
    }
  }
  *(undefined4 *)(iVar2 + 0x54) = local_c;
  if (param_1 == 8) {
    *(undefined4 *)(iVar2 + 0x58) = local_10;
  }
  return 0;
}
