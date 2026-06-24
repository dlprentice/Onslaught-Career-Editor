/* address: 0x00479db0 */
/* name: CExplosionInitThing__TriggerRandomGillArmSubEffect */
/* signature: void __fastcall CExplosionInitThing__TriggerRandomGillArmSubEffect(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CExplosionInitThing__TriggerRandomGillArmSubEffect(int param_1)

{
  byte bVar1;
  undefined4 *puVar2;
  void *pvVar3;
  float fVar4;
  float fVar5;
  uint uVar6;
  byte *pbVar7;
  int iVar8;
  undefined4 *puVar9;
  char *pcVar10;
  bool bVar11;

  if (*(float *)(param_1 + 0x26c) < DAT_00672fd0) {
    uVar6 = Random__NextLCGAbs(DAT_008a9d9c);
    fVar5 = _DAT_005d85ec;
    uVar6 = uVar6 & 0x8000ffff;
    if ((int)uVar6 < 0) {
      uVar6 = (uVar6 - 1 | 0xffff0000) + 1;
    }
    fVar4 = (float)(int)uVar6 * _DAT_005d8d54;
    puVar2 = *(undefined4 **)(param_1 + 0x19c);
    if (puVar2 == (undefined4 *)0x0) {
      puVar9 = (undefined4 *)0x0;
    }
    else {
      puVar9 = (undefined4 *)*puVar2;
    }
    while (puVar9 != (undefined4 *)0x0) {
      pvVar3 = (void *)*puVar9;
      if (pvVar3 != (void *)0x0) {
        if (fVar4 <= fVar5) {
          pcVar10 = s_Gill_M_Left_Arm_0062ca20;
          pbVar7 = *(byte **)(*(int *)((int)pvVar3 + 0x164) + 0xb0);
          do {
            bVar1 = *pbVar7;
            bVar11 = bVar1 < (byte)*pcVar10;
            if (bVar1 != *pcVar10) {
LAB_00479eab:
              iVar8 = (1 - (uint)bVar11) - (uint)(bVar11 != 0);
              goto joined_r0x00479eb2;
            }
            if (bVar1 == 0) break;
            bVar1 = pbVar7[1];
            bVar11 = bVar1 < (byte)pcVar10[1];
            if (bVar1 != pcVar10[1]) goto LAB_00479eab;
            pbVar7 = pbVar7 + 2;
            pcVar10 = pcVar10 + 2;
          } while (bVar1 != 0);
          iVar8 = 0;
        }
        else {
          pcVar10 = s_Gill_M_Right_Arm_0062ca30;
          pbVar7 = *(byte **)(*(int *)((int)pvVar3 + 0x164) + 0xb0);
          do {
            bVar1 = *pbVar7;
            bVar11 = bVar1 < (byte)*pcVar10;
            if (bVar1 != *pcVar10) {
LAB_00479e6b:
              iVar8 = (1 - (uint)bVar11) - (uint)(bVar11 != 0);
              goto joined_r0x00479eb2;
            }
            if (bVar1 == 0) break;
            bVar1 = pbVar7[1];
            bVar11 = bVar1 < (byte)pcVar10[1];
            if (bVar1 != pcVar10[1]) goto LAB_00479e6b;
            pbVar7 = pbVar7 + 2;
            pcVar10 = pcVar10 + 2;
          } while (bVar1 != 0);
          iVar8 = 0;
        }
joined_r0x00479eb2:
        if (iVar8 == 0) {
          CExplosionInitThing__Helper_00428cb0(pvVar3);
        }
      }
      puVar2 = (undefined4 *)puVar2[1];
      if (puVar2 == (undefined4 *)0x0) {
        puVar9 = (undefined4 *)0x0;
      }
      else {
        puVar9 = (undefined4 *)*puVar2;
      }
    }
    *(float *)(param_1 + 0x26c) = DAT_00672fd0 + _DAT_005d8bf4;
  }
  return;
}
