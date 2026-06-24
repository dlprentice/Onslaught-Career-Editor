/* address: 0x00591cb0 */
/* name: CTexture__Unk_00591cb0 */
/* signature: int __stdcall CTexture__Unk_00591cb0(void * param_1) */


int CTexture__Unk_00591cb0(void *param_1)

{
  undefined1 uVar1;
  byte bVar2;
  undefined4 *puVar3;
  int iVar4;
  undefined4 *puVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  undefined4 extraout_EAX;
  int iVar9;
  ushort uVar10;
  uint uVar11;
  ushort *puVar12;
  undefined1 *puVar13;
  byte *pbVar14;
  int *piStack_c;

  puVar3 = *(undefined4 **)((int)param_1 + 0x18);
  iVar8 = puVar3[1];
  puVar13 = (undefined1 *)*puVar3;
  if (iVar8 == 0) {
    iVar8 = (*(code *)puVar3[3])(param_1);
    if (iVar8 == 0) {
      return 0;
    }
    puVar13 = (undefined1 *)*puVar3;
    iVar8 = puVar3[1];
  }
  uVar1 = *puVar13;
  iVar8 = iVar8 + -1;
  puVar13 = puVar13 + 1;
  if (iVar8 == 0) {
    iVar8 = (*(code *)puVar3[3])(param_1);
    if (iVar8 == 0) {
      return 0;
    }
    puVar13 = (undefined1 *)*puVar3;
    iVar8 = puVar3[1];
  }
  iVar8 = iVar8 + -1;
  pbVar14 = puVar13 + 1;
  iVar4 = CONCAT11(uVar1,*puVar13) - 2;
  do {
    iVar7 = iVar4;
    if (iVar7 < 1) {
      if (iVar7 != 0) {
        puVar5 = *(undefined4 **)param_1;
        puVar5[5] = 0xb;
        (*(code *)*puVar5)(param_1);
      }
      *puVar3 = pbVar14;
      puVar3[1] = iVar8;
      return 1;
    }
    if (iVar8 == 0) {
      iVar8 = (*(code *)puVar3[3])(param_1);
      if (iVar8 == 0) {
        return 0;
      }
      pbVar14 = (byte *)*puVar3;
      iVar8 = puVar3[1];
    }
    bVar2 = *pbVar14;
    iVar4 = *(int *)param_1;
    iVar9 = (int)(uint)bVar2 >> 4;
    *(undefined4 *)(iVar4 + 0x14) = 0x51;
    uVar11 = bVar2 & 0xf;
    *(uint *)(iVar4 + 0x18) = uVar11;
    iVar8 = iVar8 + -1;
    pbVar14 = pbVar14 + 1;
    *(int *)(iVar4 + 0x1c) = iVar9;
    (**(code **)(iVar4 + 4))(param_1,1);
    if (3 < uVar11) {
      puVar5 = *(undefined4 **)param_1;
      puVar5[5] = 0x1f;
      puVar5[6] = uVar11;
      (*(code *)*puVar5)(param_1);
    }
    if (*(int *)((int)param_1 + uVar11 * 4 + 0xa8) == 0) {
      CTexture__Helper_0059c630((int)param_1);
      *(undefined4 *)((int)param_1 + uVar11 * 4 + 0xa8) = extraout_EAX;
    }
    iVar4 = *(int *)((int)param_1 + uVar11 * 4 + 0xa8);
    piStack_c = &DAT_005f37f8;
    do {
      if (iVar9 == 0) {
        if (iVar8 == 0) {
          iVar8 = (*(code *)puVar3[3])(param_1);
          if (iVar8 == 0) {
            return 0;
          }
          pbVar14 = (byte *)*puVar3;
          iVar8 = puVar3[1];
        }
        uVar10 = (ushort)*pbVar14;
      }
      else {
        if (iVar8 == 0) {
          iVar8 = (*(code *)puVar3[3])(param_1);
          if (iVar8 == 0) {
            return 0;
          }
          pbVar14 = (byte *)*puVar3;
          iVar8 = puVar3[1];
        }
        bVar2 = *pbVar14;
        iVar8 = iVar8 + -1;
        pbVar14 = pbVar14 + 1;
        if (iVar8 == 0) {
          iVar8 = (*(code *)puVar3[3])(param_1);
          if (iVar8 == 0) {
            return 0;
          }
          pbVar14 = (byte *)*puVar3;
          iVar8 = puVar3[1];
        }
        uVar10 = (ushort)bVar2 * 0x100 + (ushort)*pbVar14;
      }
      iVar6 = *piStack_c;
      iVar8 = iVar8 + -1;
      piStack_c = piStack_c + 1;
      pbVar14 = pbVar14 + 1;
      *(ushort *)(iVar4 + iVar6 * 2) = uVar10;
    } while ((int)piStack_c < 0x5f38f8);
    if (1 < *(int *)(*(int *)param_1 + 0x68)) {
      puVar12 = (ushort *)(iVar4 + 4);
      piStack_c = (int *)0x8;
      do {
        iVar4 = *(int *)param_1;
        *(uint *)(iVar4 + 0x18) = (uint)puVar12[-2];
        *(uint *)(iVar4 + 0x1c) = (uint)puVar12[-1];
        *(uint *)(iVar4 + 0x20) = (uint)*puVar12;
        *(uint *)(iVar4 + 0x24) = (uint)puVar12[1];
        *(uint *)(iVar4 + 0x28) = (uint)puVar12[2];
        *(uint *)(iVar4 + 0x2c) = (uint)puVar12[3];
        *(uint *)(iVar4 + 0x30) = (uint)puVar12[4];
        *(uint *)(iVar4 + 0x34) = (uint)puVar12[5];
        *(undefined4 *)(iVar4 + 0x14) = 0x5d;
        (**(code **)(iVar4 + 4))(param_1,2);
        puVar12 = puVar12 + 8;
        piStack_c = (int *)((int)piStack_c + -1);
      } while (piStack_c != (int *)0x0);
    }
    iVar4 = iVar7 + -0x41;
    if (iVar9 != 0) {
      iVar4 = iVar7 + -0x81;
    }
  } while( true );
}
