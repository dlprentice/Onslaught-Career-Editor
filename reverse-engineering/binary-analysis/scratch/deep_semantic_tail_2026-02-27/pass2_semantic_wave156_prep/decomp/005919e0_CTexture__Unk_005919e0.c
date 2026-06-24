/* address: 0x005919e0 */
/* name: CTexture__Unk_005919e0 */
/* signature: int CTexture__Unk_005919e0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Unk_005919e0(void)

{
  byte bVar1;
  undefined4 *puVar2;
  uint *puVar3;
  int iVar4;
  uint uVar5;
  int extraout_EAX;
  int *unaff_EBX;
  byte *pbVar6;
  int iVar7;
  int *piVar8;
  byte *pbVar9;
  undefined4 *puVar10;
  int iStack_128;
  undefined4 local_124;
  uint uStack_120;
  uint uStack_11c;
  uint uStack_118;
  uint uStack_114;
  undefined4 *puStack_110;
  undefined1 uStack_10c;
  undefined4 *local_108;
  uint uStack_104;
  byte abStack_100 [256];

  puVar2 = (undefined4 *)unaff_EBX[6];
  iStack_128 = puVar2[1];
  pbVar6 = (byte *)*puVar2;
  local_108 = puVar2;
  if (iStack_128 == 0) {
    iVar4 = (*(code *)puVar2[3])();
    if (iVar4 == 0) {
      return 0;
    }
    iStack_128 = puVar2[1];
    pbVar6 = (byte *)*puVar2;
  }
  local_124 = (uint)*pbVar6 << 8;
  iStack_128 = iStack_128 + -1;
  pbVar6 = pbVar6 + 1;
  if (iStack_128 == 0) {
    iVar4 = (*(code *)puVar2[3])();
    if (iVar4 == 0) {
      return 0;
    }
    iStack_128 = puVar2[1];
    pbVar6 = (byte *)*puVar2;
  }
  iStack_128 = iStack_128 + -1;
  local_124 = (local_124 + *pbVar6) - 2;
  pbVar6 = pbVar6 + 1;
  do {
    if ((int)local_124 < 0x11) {
      if (local_124 != 0) {
        puVar10 = (undefined4 *)*unaff_EBX;
        puVar10[5] = 0xb;
        (*(code *)*puVar10)();
      }
      *puVar2 = pbVar6;
      puVar2[1] = iStack_128;
      return 1;
    }
    if (iStack_128 == 0) {
      iVar4 = (*(code *)puVar2[3])();
      if (iVar4 == 0) {
        return 0;
      }
      iStack_128 = puVar2[1];
      pbVar6 = (byte *)*puVar2;
    }
    uStack_104 = (uint)*pbVar6;
    iVar4 = *unaff_EBX;
    iVar7 = iStack_128 + -1;
    *(undefined4 *)(iVar4 + 0x14) = 0x50;
    pbVar6 = pbVar6 + 1;
    *(uint *)(iVar4 + 0x18) = uStack_104;
    (**(code **)(iVar4 + 4))();
    local_124 = local_124 & 0xffffff00;
    iStack_128 = 0;
    iVar4 = 1;
    do {
      puVar2 = puStack_110;
      if (iVar7 == 0) {
        iVar7 = (*(code *)puStack_110[3])();
        if (iVar7 == 0) {
          return 0;
        }
        iVar7 = puVar2[1];
        pbVar6 = (byte *)*puVar2;
      }
      bVar1 = *pbVar6;
      *(byte *)((int)&local_124 + iVar4) = bVar1;
      iVar7 = iVar7 + -1;
      iStack_128 = iStack_128 + (uint)bVar1;
      pbVar6 = pbVar6 + 1;
      iVar4 = iVar4 + 1;
    } while (iVar4 < 0x11);
    iVar4 = *unaff_EBX;
    *(uint *)(iVar4 + 0x18) = local_124 >> 8 & 0xff;
    *(uint *)(iVar4 + 0x1c) = local_124 >> 0x10 & 0xff;
    *(uint *)(iVar4 + 0x20) = local_124 >> 0x18;
    *(uint *)(iVar4 + 0x24) = uStack_120 & 0xff;
    *(uint *)(iVar4 + 0x28) = uStack_120 >> 8 & 0xff;
    *(uint *)(iVar4 + 0x2c) = uStack_120 >> 0x10 & 0xff;
    *(uint *)(iVar4 + 0x30) = uStack_120 >> 0x18;
    *(uint *)(iVar4 + 0x34) = uStack_11c & 0xff;
    *(undefined4 *)(iVar4 + 0x14) = 0x56;
    (**(code **)(iVar4 + 4))();
    iVar4 = *unaff_EBX;
    *(uint *)(iVar4 + 0x18) = local_124 >> 8 & 0xff;
    *(uint *)(iVar4 + 0x1c) = local_124 >> 0x10 & 0xff;
    *(uint *)(iVar4 + 0x20) = local_124 >> 0x18;
    *(uint *)(iVar4 + 0x24) = uStack_120 & 0xff;
    *(uint *)(iVar4 + 0x28) = uStack_120 >> 8 & 0xff;
    *(uint *)(iVar4 + 0x2c) = uStack_120 >> 0x10 & 0xff;
    *(uint *)(iVar4 + 0x30) = uStack_120 >> 0x18;
    *(uint *)(iVar4 + 0x34) = uStack_11c & 0xff;
    *(undefined4 *)(iVar4 + 0x14) = 0x56;
    (**(code **)(iVar4 + 4))();
    if ((0x100 < (int)uStack_120) || ((int)local_124 < (int)uStack_120)) {
      puVar2 = (undefined4 *)*unaff_EBX;
      puVar2[5] = 8;
      (*(code *)*puVar2)();
    }
    iVar4 = 0;
    uVar5 = uStack_120;
    if (0 < (int)uStack_120) {
      do {
        puVar2 = local_108;
        if (iVar7 == 0) {
          iVar7 = (*(code *)local_108[3])();
          if (iVar7 == 0) {
            return 0;
          }
          iVar7 = puVar2[1];
          pbVar6 = (byte *)*puVar2;
          uVar5 = uStack_120;
        }
        bVar1 = *pbVar6;
        iVar7 = iVar7 + -1;
        pbVar6 = pbVar6 + 1;
        abStack_100[iVar4] = bVar1;
        iVar4 = iVar4 + 1;
        iStack_128 = iVar7;
      } while (iVar4 < (int)uVar5);
    }
    local_124 = local_124 - uVar5;
    if ((uStack_104 & 0x10) == 0) {
      iVar4 = uStack_104 + 0x2e;
      uVar5 = uStack_104;
    }
    else {
      iVar4 = uStack_104 + 0x22;
      uVar5 = uStack_104 - 0x10;
    }
    piVar8 = unaff_EBX + iVar4;
    if (((int)uVar5 < 0) || (3 < (int)uVar5)) {
      puVar2 = (undefined4 *)*unaff_EBX;
      puVar2[5] = 0x1e;
      puVar2[6] = uVar5;
      (*(code *)*puVar2)();
    }
    if (*piVar8 == 0) {
      CTexture__Helper_0059c650((int)unaff_EBX);
      *piVar8 = extraout_EAX;
    }
    puVar3 = (uint *)*piVar8;
    *puVar3 = uStack_11c;
    puVar3[1] = uStack_118;
    puVar3[2] = uStack_114;
    puVar3[3] = (uint)puStack_110;
    *(undefined1 *)(puVar3 + 4) = uStack_10c;
    pbVar9 = abStack_100;
    puVar10 = (undefined4 *)((int)puVar3 + 0x11);
    for (iVar4 = 0x40; puVar2 = local_108, iVar4 != 0; iVar4 = iVar4 + -1) {
      *puVar10 = *(undefined4 *)pbVar9;
      pbVar9 = pbVar9 + 4;
      puVar10 = puVar10 + 1;
    }
  } while( true );
}
